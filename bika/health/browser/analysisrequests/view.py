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
from bika.lims.utils import get_link
from plone.memoize import view as viewcache


class AnalysisRequestsView(BaseView):
    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
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
            self.remove_column('getPatientID')
            self.remove_column('getClientPatientID')
            self.remove_column('getPatient')
            self.remove_column('getDoctor')
        # Otherwise show the columns in the list
        else:
            for rs in self.review_states:
                i = rs['columns'].index('BatchID') + 1
                rs['columns'].insert(i, 'getClientPatientID')
                rs['columns'].insert(i, 'getPatientID')
                rs['columns'].insert(i, 'getPatient')
                rs['columns'].insert(i, 'getDoctor')
        return super(AnalysisRequestsView, self).folderitems(
            full_objects=False, classic=False)

    @viewcache.memoize
    def get_brain(self, uid, catalog):
        if not api.is_uid(uid):
            return None
        query = dict(UID=uid)
        brains = api.search(query, catalog)
        if brains and len(brains) == 1:
            return brains[0]
        return None

    def folderitem(self, obj, item, index):
        item = super(AnalysisRequestsView, self)\
            .folderitem(obj, item, index)
        patient = self.get_brain(obj.getPatientUID, CATALOG_PATIENT_LISTING)
        if patient:
            cpid = patient.getClientPatientID
            url = '%s/analysisrequests' % api.get_url(patient)
            item['getPatientID'] = patient.getId
            item['getClientPatientID'] = patient.getClientPatientID
            item['getPatient'] = patient.Title
            item['replace']['getPatientID'] = get_link(url, patient.getId)
            item['replace']['getClientPatientID'] = get_link(url, cpid)
            item['replace']['getPatient'] = get_link(url, patient.Title)

        doctor = self.get_brain(obj.getDoctorUID, "portal_catalog")
        if doctor:
            url = '%s/analysisrequests' % api.get_url(doctor)
            item['getDoctor'] = doctor.Title
            item['replace']['getDoctor'] = get_link(url, doctor.Title)
        return item
