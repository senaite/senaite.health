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
from Products.CMFCore.utils import getToolByName
import json

from bika.health.interfaces import IPatient


class PatientMenstrualStatusWidget(ATRecordsWidget):
    security = ClassSecurityInfo()
    _properties = ATRecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_health_widgets/patientmenstrualstatuswidget",
        'helper_js': ("bika_health_widgets/patientmenstrualstatuswidget.js",),
        'helper_css': ("bika_health_widgets/patientmenstrualstatuswidget.css",),
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        outvalues = []
        values = form.get(field.getName(), empty_marker)
        for value in values:
            outvalues.append({'Hysterectomy': bool(value.get('Hysterectomy', False)),
                              'HysterectomyYear': value.get('HysterectomyYear', ''),
                              'OvariesRemoved': bool(value.get('OvariesRemoved', False)),
                              'OvariesRemovedNum': int(value.get('OvariesRemovedNum', 0)),
                              'OvariesRemovedYear': value.get('OvariesRemovedYear', '')})
        return outvalues, {}

    def jsondumps(self, val):
        return json.dumps(val)

    def getPatientsGender(self):
        patient = self.aq_parent
        return IPatient.providedBy(patient) and patient.getGender() or "dk"

    def getMenstrualStatus(self):

        statuses = [{'Hysterectomy': False,
                     'HysterectomyYear': '',
                     'OvariesRemoved': False,
                     'OvariesRemovedNum': 0,
                     'OvariesRemovedYear': ''}]

        return len(self.aq_parent.getMenstrualStatus()) > 0 \
                    and self.aq_parent.getMenstrualStatus() \
                    or statuses

registerWidget(PatientMenstrualStatusWidget,
               title='PatientMenstrualStatusWidget',
               description='Menstrual status information',
               )
