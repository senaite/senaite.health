# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser.analysisrequest import AnalysisRequestsView as BaseView
from bika.health import bikaMessageFactory as _
from Products.CMFCore.utils import getToolByName
from bika.health.catalog import CATALOG_PATIENT_LISTING


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
        # Setting ip the patient catalog to be used in folderitem()
        self.patient_catalog = getToolByName(
            self.context, CATALOG_PATIENT_LISTING)
        return super(AnalysisRequestsView, self).folderitems(
            full_objects=False, classic=False)

    def folderitem(self, obj, item, index):
        item = super(AnalysisRequestsView, self)\
            .folderitem(obj, item, index)
        patient = self.patient_catalog(UID=obj.getPatientUID)
        if patient:
            item['getPatientID'] = patient[0].getId
            item['replace']['getPatientID'] = "<a href='%s'>%s</a>" % \
                (patient[0].getURL(), patient[0].getId)
            item['getClientPatientID'] = patient[0].getClientPatientID
            item['replace']['getClientPatientID'] = "<a href='%s'>%s</a>" % \
                (patient[0].getURL(), patient[0].getClientPatientID)
            item['getPatient'] = patient[0].Title
            item['replace']['getPatient'] = "<a href='%s'>%s</a>" % \
                (patient[0].getURL(), patient[0].Title)
        return item
