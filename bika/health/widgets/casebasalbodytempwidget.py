# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.widget import RecordsWidget as ATRecordsWidget
from Products.Archetypes.Registry import registerWidget
import json


class CaseBasalBodyTempWidget(ATRecordsWidget):
    security = ClassSecurityInfo()
    _properties = ATRecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_health_widgets/casebasalbodytempwidget",
        'helper_js': ("bika_health_widgets/casebasalbodytempwidget.js",),
        'helper_css': ("bika_health_widgets/casebasalbodytempwidget.css",),
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        outvalues = []
        values = form.get(field.getName(), empty_marker)
        for value in values:
            outvalues.append({'Day1': value.get('Day1', ''),
                              'Day2': value.get('Day2', ''),
                              'Day3': value.get('Day3', '')})
        return outvalues, {}

    def jsondumps(self, val):
        return json.dumps(val)

    def getBasalBodyTemperature(self):
        conditions = [{'Day1': '',
                       'Day2': '',
                       'Day3': ''}]
        field = self.aq_parent.Schema()['BasalBodyTemperature']
        value = field.get(self.aq_parent)
        return value and value or conditions

registerWidget(CaseBasalBodyTempWidget,
               title='CaseBasalBodyTempWidget',
               description='Basal body temperature',)
