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

from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.lims import bikaMessageFactory as _b
from bika.lims.browser import BrowserView
from bika.lims.permissions import *
import json
import plone


class ajaxGetBatchInfo(BrowserView):
    """ Grab the details for Doctor, Patient, Hospital (Titles).
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        batch = self.context
        client = batch.getClient()
        doctor = batch.Schema()['Doctor'].get(batch)
        patient = batch.Schema()['Patient'].get(batch)

        ret = {'ClientID': client and client.getClientID() or '',
               'ClientSysID': client and client.id or '',
               'ClientUID': client and client.UID() or '',
               'ClientTitle': client and client.Title() or '',
               'PatientID': patient and patient.getPatientID() or '',
               'PatientUID': patient and patient.UID() or '',
               'PatientTitle': patient and patient.Title() or '',
               'ClientPatientID': patient and patient.getClientPatientID() or '',
               'DoctorID': doctor and doctor.getDoctorID(),
               'DoctorUID': doctor and doctor.UID() or '',
               'DoctorTitle': doctor and doctor.Title() or ''}

        return json.dumps(ret)
