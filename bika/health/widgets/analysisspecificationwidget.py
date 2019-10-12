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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.CMFCore.utils import getToolByName
from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator
from zope.interface import implements

from bika.health import api
from bika.health import bikaMessageFactory as _
from bika.lims.browser.widgets.analysisspecificationwidget import \
    AnalysisSpecificationView as BaseView, \
    AnalysisSpecificationWidget as BaseWidget


class AnalysisSpecificationView(BaseView):

    def __init__(self, context, request):
        super(AnalysisSpecificationView, self).__init__(context, request)

        self.columns['minpanic'] = {'title': _('Min panic'), 'sortable': False}
        self.columns['maxpanic'] = {'title': _('Max panic'), 'sortable': False}
        self.review_states[0]['columns'] += ['minpanic', 'maxpanic']

    def folderitem(self, obj, item, index):
        item = super(AnalysisSpecificationView, self).folderitem(obj, item, index)
        obj = api.get_object(obj)
        keyword = obj.getKeyword()
        spec = self.specification.get(keyword, {})
        item['minpanic'] = spec.get("minpanic", "")
        item['maxpanic'] = spec.get("maxpanic", "")
        return item

    def get_editable_columns(self):
        """Return editable fields
        """
        cols = super(AnalysisSpecificationView, self).get_editable_columns()
        cols.extend(["minpanic", "maxpanic"])
        return cols


class AnalysisSpecificationWidget(BaseWidget):
    _properties = BaseWidget._properties.copy()

    security = ClassSecurityInfo()

    security.declarePublic('process_form')

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """Return a list of dictionaries fir for AnalysisSpecsResultsField
        consumption.
        """
        values = BaseWidget.process_form(self, instance, field, form,
                                         empty_marker, emptyReturnsMarker)
        for value in values[0]:
            uid = value["uid"]
            value["minpanic"] = self._get_spec_value(form, uid, "minpanic")
            value["maxpanic"] = self._get_spec_value(form, uid, "maxpanic")
        return values[0], {}


registerWidget(AnalysisSpecificationWidget,
               title='Analysis Specification Results',
               description=('Analysis Specification Results'))


class AnalysisSpecificationPanicValidator(object):
    implements(IValidator)
    name = "analysisspecs_panic_validator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        ts = getToolByName(instance, 'translation_service').translate

        if instance.REQUEST.get('validated', '') == self.name:
            return True
        else:
            instance.REQUEST['validated'] = self.name
        pmins = instance.REQUEST.get('minpanic', {})
        if len(pmins) > 0:
            pmins = pmins[0]
        pmaxs = instance.REQUEST.get('maxpanic', {})
        if len(pmaxs) > 0:
            pmaxs = pmaxs[0]
        uids = pmins.keys()
        for uid in uids:
            pmin = pmins.get(uid, '') == '' and '0' or pmins[uid]
            pmax = pmaxs.get(uid, '') == '' and '0' or pmaxs[uid]

            # Values must be numbers
            try:
                pmin = float(pmin)
            except:
                return ts(_("Validation failed: Panic min value must be "
                            "numeric"))

            try:
                pmax = float(pmax)
            except:
                return ts(_("Validation failed: Panic min value must be "
                            "numeric"))

            if pmin > pmax:
                return ts(_("Validation failed: Panic max value must be "
                            "greater than panic min value"))
        return True


validation.register(AnalysisSpecificationPanicValidator())
