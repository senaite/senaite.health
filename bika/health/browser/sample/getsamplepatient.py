# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json

import plone
from Products.CMFCore.utils import getToolByName

from bika.lims.api import get_object
from bika.lims.browser import BrowserView


class ajaxGetSamplePatient(BrowserView):
    """ Returns the patient assigned to the newest AnalysisRequest with
        a patient assigned.
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        uid = self.request.get('uid', '')
        ret = {}
        if uid:
            uc = getToolByName(self.context, 'uid_catalog')
            proxies = uc(UID=uid)
            if proxies and len(proxies) > 0:
                sample = get_object(proxies[0])
                patient = sample.Schema().getField('Patient').get(sample)
                if patient:
                    PR = patient.getPrimaryReferrer()
                    ret = {
                        'PatientID': patient.getPatientID(),
                        'PatientUID': patient.UID(),
                        'ClientPatientID': patient.getClientPatientID(),
                        'ClientID': PR and PR.getClientID() or '',
                        'ClientUID': PR and PR.UID() or '',
                        'ClientTitle': PR and PR.Title() or '',
                        'ClientSysID' : PR and PR.id or '',
                        'PatientFullname': patient.Title(),
                        'PatientBirthDate':
                            self.ulocalized_time(patient.getBirthDate()),
                        'PatientGender': patient.getGender(),
                        'PatientMenstrualStatus': patient.getMenstrualStatus()
                        }
        return json.dumps(ret)
