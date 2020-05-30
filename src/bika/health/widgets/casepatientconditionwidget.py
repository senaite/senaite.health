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

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.widget import RecordsWidget as ATRecordsWidget
from Products.Archetypes.Registry import registerWidget
import json


class CasePatientConditionWidget(ATRecordsWidget):
    security = ClassSecurityInfo()
    _properties = ATRecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_health_widgets/casepatientconditionwidget",
        'helper_js': ("bika_health_widgets/casepatientconditionwidget.js",),
        'helper_css': ("bika_health_widgets/casepatientconditionwidget.css",),
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        # ignore records with empty values
        outvalues = []
        values = form.get(field.getName(), empty_marker)
        for value in values:
            if value.get('Value', '').strip() != '':
                outvalues.append(value)
        return outvalues, {}

    def jsondumps(self, val):
        return json.dumps(val)

    def getPatientCondition(self):
        # self.aq_parent.Schema()['Patient'].set(self.aq_parent.patients.objectValues()[0].UID())
        value = self.aq_parent.Schema()['PatientCondition'].get(self.aq_parent)
        conditions = len(value) > 0 and value or []

        # Allow multiple units for each condition. Check if existing conditions
        # don't have bika_setup already defined units
        heightunits = self.getHeightUnits()
        for unit in heightunits:
            exists = False
            for condition in conditions:
                if condition['Condition'] == 'Height' \
                    and condition['Unit'] == unit:
                    exists = True
                    break
            if not exists:
                conditions.append({'Condition': 'Height',
                               'Unit': unit,
                               'Value': ''})

        weightunits = self.getWeightUnits()
        for unit in weightunits:
            exists = False
            for condition in conditions:
                if condition['Condition'] == 'Weight' \
                    and condition['Unit'] == unit:
                    exists = True
                    break
            if not exists:
                conditions.append({'Condition': 'Weight',
                               'Unit': unit,
                               'Value': ''})

        weightunits = self.getWaistUnits()
        for unit in weightunits:
            exists = False
            for condition in conditions:
                if condition['Condition'] == 'Waist' \
                    and condition['Unit'] == unit:
                    exists = True
                    break
            if not exists:
                conditions.append({'Condition': 'Waist',
                               'Unit': unit,
                               'Value': ''})

        return conditions

    def getUnits(self, units=None):
        return (units and "/" in units) and units.split('/') or [units]

    def getHeightUnits(self):
        field = self.bika_setup.Schema()['PatientConditionsHeightUnits']
        return self.getUnits(field.get(self.bika_setup))

    def getWeightUnits(self):
        field = self.bika_setup.Schema()['PatientConditionsWeightUnits']
        return self.getUnits(field.get(self.bika_setup))

    def getWaistUnits(self):
        field = self.bika_setup.Schema()['PatientConditionsWaistUnits']
        return self.getUnits(field.get(self.bika_setup))

    def getConditionValue(self, condition, unit):
        conditions = self.getPatientCondition()
        for cond in conditions:
            if cond['Condition'] == condition \
                and cond['Unit'] == unit:
                return cond['Value']
        return ''

registerWidget(CasePatientConditionWidget,
               title='CasePatientConditionWidget',
               description='Patient Condition information',)
