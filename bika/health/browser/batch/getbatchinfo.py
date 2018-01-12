# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
        client = batch.Schema()['Client'].get(batch)
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
