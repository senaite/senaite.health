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

import json

import plone

from bika.health.catalog import CATALOG_PATIENTS
from bika.lims import api
from bika.lims.browser import BrowserView


class ajaxGetPatientInfo(BrowserView):
    """ Grab details of newly created patient (#420)
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        ret = {'PatientID': '',
               'PatientUID': '',
               'ClientPatientID': '',
               'ClientID': '',
               'ClientUID': '',
               'ClientTitle': '',
               'ClientSysID': '',
               'PatientFullname': '',
               'PatientBirthDate': '',
               'PatientGender': 'dk',
               'PatientMenstrualStatus': ''}

        uid = self.request.get('PatientUID', '')
        if not uid:
            return json.dumps(ret)

        brains = api.search({"UID": uid}, CATALOG_PATIENTS)
        if brains:
            patient = brains[0]
            ret = {
                'PatientID': patient.getPatientID,
                'PatientUID': patient.UID,
                'ClientPatientID': patient.getClientPatientID,
                'ClientUID': patient.getPrimaryReferrerUID,
                'ClientTitle': patient.getPrimaryReferrerTitle,
                'ClientSysID': patient.getPrimaryReferrerID,
                'PatientFullname': patient.Title,
                'PatientBirthDate': self.ulocalized_time(patient.getBirthDate),
                'PatientGender': patient.getGender,
                'PatientMenstrualStatus': patient.getMenstrualStatus
            }

        return json.dumps(ret)
