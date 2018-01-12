# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.widget import RecordsWidget as ATRecordsWidget
from Products.Archetypes.Registry import registerWidget
from Products.CMFCore.utils import getToolByName
import json


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
        gender = 'dk'
        patientid = self.aq_parent.getPatientID()
        if patientid:
            bpc = getToolByName(self, 'bikahealth_catalog_patient_listing')
            patient = bpc(portal_type='Patient', id=patientid)
            gender = len(patient) > 0 \
                        and patient[0].getObject().getGender() or 'dk'
        return gender

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
