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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import itertools
import json
from datetime import datetime

from Products.ATContentTypes.utils import DT2dt
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.health import bikaMessageFactory as _
from bika.lims import api
from bika.lims import to_utf8
from bika.lims.api import to_date
from bika.lims.api.analysis import get_formatted_interval
from bika.lims.browser import BrowserView
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.utils import format_supsub


class HistoricResultsView(BrowserView):
    """Historic Results View
    """
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

    # Retrieve the AR IDs for the current patient
    query = {"portal_type": "AnalysisRequest",
             "getPatientUID": api.get_uid(patient),
             "review_state": ["verified", "published"],
             "sort_on": "getDateSampled",
             "sort_order": "descending"}
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    samples = map(api.get_object, brains)

    # Retrieve all analyses
    analyses = map(lambda samp: samp.objectValues("Analysis"), samples)
    analyses = list(itertools.chain.from_iterable(analyses))

    # Build the dictionary of rows
    for analysis in analyses:
        sample = analysis.aq_parent
        sample_type = sample.getSampleType()
        row = {
            "object": sample_type,
            "analyses": {},
        }
        sample_type_uid = api.get_uid(sample_type)
        if sample_type_uid in rows:
            row = rows.get(sample_type_uid)

        anrow = row.get("analyses")
        service_uid = analysis.getServiceUID()
        asdict = {
            "object": analysis,
            "title": api.get_title(analysis),
            "keyword": to_utf8(analysis.getKeyword()),
        }
        if service_uid in anrow:
            asdict = anrow.get(service_uid)

        if not anrow.get("units", None):
            asdict.update({
                "units": format_supsub(to_utf8(analysis.getUnit()))
            })

        date = analysis.getResultCaptureDate() or analysis.created()
        date_time = DT2dt(to_date(date)).replace(tzinfo=None)
        date_time = datetime.strftime(date_time, "%Y-%m-%d %H:%M")

        # If more than one analysis of the same type has been
        # performed in the same datetime, get only the last one
        if date_time not in asdict.keys():
            asdict[date_time] = {
                "object": analysis,
                "result": analysis.getResult(),
                "formattedresult": analysis.getFormattedResult()
            }
            # Get the specs
            # Only the specs applied to the last analysis for that
            # sample type will be taken into consideration.
            # We assume specs from previous analyses are obsolete.
            if "specs" not in asdict.keys():
                specs = analysis.getResultsRange()
                asdict["specs"] = get_formatted_interval(specs, "")

            if date_time not in dates:
                dates.append(date_time)

        anrow[service_uid] = asdict
        row['analyses'] = anrow
        rows[sample_type_uid] = row
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
            datarow = {'date': andate}
            for row in data.itervalues():
                for anrow in row['analyses'].itervalues():
                    serie = anrow['title']
                    if "result" not in anrow.get(andate, {}):
                        continue
                    datarow[serie] = anrow.get(andate, {}).get('result', '')
            datatable.append(datarow)
        return json.dumps(datatable)
