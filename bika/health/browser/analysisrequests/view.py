# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.browser.analysisrequest import AnalysisRequestsView as BaseView
from bika.health import bikaMessageFactory as _
from Products.CMFCore.utils import getToolByName
from bika.health.catalog import CATALOG_PATIENT_LISTING
from plone.memoize import view as viewcache


class AnalysisRequestsView(BaseView):
    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.patient_catalog = None
        self.columns['BatchID']['title'] = _('Case ID')
        # Add Client Patient fields
        self.columns['getPatientID'] = {
            'title': _('Patient ID'), }
        self.columns['getClientPatientID'] = {
            'title': _("Client PID"),
            'sortable': False, }
        self.columns['getPatient'] = {
            'title': _('Patient'), }
        self.columns['getDoctor'] = {
            'title': _('Doctor'), }

    def folderitems(self, full_objects=False):
        pm = getToolByName(self.context, "portal_membership")
        member = pm.getAuthenticatedMember()
        # We will use this list for each element
        roles = member.getRoles()
        # delete roles user doesn't have permissions
        if 'Manager' not in roles \
            and 'LabManager' not in roles \
                and 'LabClerk' not in roles:
            del self.columns['getPatientID']
            del self.columns['getClientPatientID']
            del self.columns['getPatient']
        # Otherwise show the columns in the list
        else:
            for rs in self.review_states:
                i = rs['columns'].index('BatchID') + 1
                rs['columns'].insert(i, 'getClientPatientID')
                rs['columns'].insert(i, 'getPatientID')
                rs['columns'].insert(i, 'getPatient')
                rs['columns'].insert(i, 'getDoctor')
        # Setting ip the patient catalog to be used in folderitem()
        self.patient_catalog = getToolByName(
            self.context, CATALOG_PATIENT_LISTING)
        return super(AnalysisRequestsView, self).folderitems(
            full_objects=False, classic=False)

    @viewcache.memoize
    def get_patient_brain(self, patient_uid):
        query = dict(UID=patient_uid)
        patient = api.search(query, CATALOG_PATIENT_LISTING)
        if patient and len(patient) == 1:
            return patient[0]
        return None

    def folderitem(self, obj, item, index):
        item = super(AnalysisRequestsView, self)\
            .folderitem(obj, item, index)
        patient = self.get_patient_brain(obj.getPatientUID)
        if patient:
            item['getPatientID'] = patient.getId
            item['replace']['getPatientID'] = "<a href='%s/analysisrequests'>%s</a>" % \
                (patient.getURL(), patient.getId)
            item['getClientPatientID'] = patient.getClientPatientID
            item['replace']['getClientPatientID'] = "<a href='%s/analysisrequests'>%s</a>" % \
                (patient.getURL(), patient.getClientPatientID)
            item['getPatient'] = patient[0].Title
            item['replace']['getPatient'] = "<a href='%s/analysisrequests'>%s</a>" % \
                (patient.getURL(), patient.Title)
        doctor_uid = obj.getDoctorUID
        if doctor_uid:
            doctor = api.get_object_by_uid(doctor_uid)
            if doctor:
                item['getDoctor'] = doctor.Title()
                item['replace']['getDoctor'] = "<a href='%s/analysisrequests'>%s</a>" % \
                                                (api.get_url(doctor),
                                                 doctor.Title())
        return item
