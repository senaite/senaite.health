# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH.
#
# SENAITE.HEALTH is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser import BrowserView
from bika.health import bikaMessageFactory as _
from zope.interface import implements
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFPlone.i18nl10n import ulocalized_time
import plone
import json


class HistoricResultsView(BrowserView):
    implements(IViewView)

    template = ViewPageTemplateFile("historicresults.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request
        self._rows = None
        self._dates = None
        path = "/++resource++bika.health.images"
        self.icon = self.portal_url + path + "/historicresults_big.png"
        self.title = self.context.translate(_("Historic Results"))
        self.description = ""

    def __call__(self):
        self._load()
        return self.template()

    def get_dates(self):
        """ Gets the result capture dates for which at least one analysis
            result has been found for the current Patient.
        """
        return self._dates

    def get_rows(self):
        """ Returns a dictionary with rows with the following structure:
            rows = {<sampletype_uid>: {
                        'object': <sampletype>,
                        'analyses': {
                            <analysisservice_uid>: {
                                'object': <analysisservice>,
                                'title': <analysisservice.title>,
                                'units': <analysisservice.units>,
                                'specs': {'error', 'min', 'max', ...},
                                <date> : {
                                    'object': <analysis>,
                                    'result': <analysis.result>,
                                    'date': <analysis.resultdate>
                                },
                            }
                        }
                    }}
        """
        return self._rows

    def _load(self):
        """ Loads the Controller acessors and other stuff
        """
        self._dates, self._rows = get_historicresults(self.context)


def get_historicresults(patient):
    if not patient:
        return [], {}

    rows = {}
    dates = []
    uid = patient.UID()
    states = ['verified', 'published']

    # Retrieve the AR IDs for the current patient
    bc = getToolByName(patient, 'bika_catalog')
    ars = [ar.id for ar
           in bc(portal_type='AnalysisRequest', review_state=states)
           if 'Patient' in ar.getObject().Schema()
           and ar.getObject().Schema().getField('Patient').get(ar.getObject())
           and ar.getObject().Schema().getField('Patient').get(ar.getObject()).UID() == uid]

    # Retrieve all the analyses, sorted by ResultCaptureDate DESC
    bc = getToolByName(patient, 'bika_analysis_catalog')
    analyses = [an.getObject() for an
                in bc(portal_type='Analysis',
                      getRequestID=ars,
                      sort_on='getResultCaptureDate',
                      sort_order='reverse')]

    # Build the dictionary of rows
    for analysis in analyses:
        ar = analysis.aq_parent
        sampletype = ar.getSampleType()
        row = rows.get(sampletype.UID()) if sampletype.UID() in rows.keys() \
            else {'object': sampletype, 'analyses': {}}
        anrow = row.get('analyses')
        service_uid = analysis.getServiceUID()
        asdict = anrow.get(service_uid, {'object': analysis,
                                         'title': analysis.Title(),
                                         'keyword': analysis.getKeyword(),
                                         'units': analysis.getUnit()})
        date = analysis.getResultCaptureDate() or analysis.created()
        date = ulocalized_time(date, 1, None, patient, 'bika')
        # If more than one analysis of the same type has been
        # performed in the same datetime, get only the last one
        if date not in asdict.keys():
            asdict[date] = {'object': analysis,
                            'result': analysis.getResult(),
                            'formattedresult': analysis.getFormattedResult()}
            # Get the specs
            # Only the specs applied to the last analysis for that
            # sample type will be taken into consideration.
            # We assume specs from previous analyses are obsolete.
            if 'specs' not in asdict.keys():
                spec = analysis.getAnalysisSpecs()                
                spec = spec.getResultsRangeDict() if spec else {}
                specs = spec.get(analysis.getKeyword(), {})
                if not specs.get('rangecomment', ''):
                    if specs.get('min', '') and specs.get('max', ''):
                        specs['rangecomment'] = '%s - %s' % \
                            (specs.get('min'), specs.get('max'))
                    elif specs.get('min', ''):
                        specs['rangecomment'] = '> %s' % specs.get('min')
                    elif specs.get('max', ''):
                        specs['rangecomment'] = '< %s' % specs.get('max')

                    if specs.get('error', '0') != '0' \
                            and specs.get('rangecomment', ''):
                        specs['rangecomment'] = ('%s (%s' %
                                                 (specs.get('rangecomment'),
                                                  specs.get('error'))) + '%)'
                asdict['specs'] = specs

            if date not in dates:
                dates.append(date)
        anrow[service_uid] = asdict
        row['analyses'] = anrow
        rows[sampletype.UID()] = row
    dates.sort(reverse=False)

    return dates, rows


class historicResultsJSON(BrowserView):
    """ Returns a JSON array datatable in a tabular format.
    """

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        dates, data = get_historicresults(self.context)
        datatable = []
        for andate in dates:
            datarow = {'date': ulocalized_time(
                andate, 1, None, self.context, 'bika')}
            for row in data.itervalues():
                for anrow in row['analyses'].itervalues():
                    serie = anrow['title']
                    datarow[serie] = anrow.get(andate, {}).get('result', '')
            datatable.append(datarow)
        return json.dumps(datatable)
