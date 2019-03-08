# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.health import logger
from bika.lims import api
from bika.lims.browser.analysisrequest import AnalysisRequestAddView as ARAdd
from bika.lims.browser.analysisrequest import AnalysisRequestsView as BaseView
from bika.lims.utils import get_link
from plone.memoize import view as viewcache


class AnalysisRequestAddView(ARAdd):
    """Dummy class to allow redirection when client tries to
    create an Analysis Request from analysisrequests base folder
    """
    def __call__(self):
        client = api.get_current_client()
        if client:
            url = api.get_url(client)
            ar_count = self.get_ar_count()
            return self.request.response.redirect("{}/ar_add?ar_count={}"
                                                  .format(url, ar_count))
        return super(AnalysisRequestAddView, self).__call__()


class AnalysisRequestsView(BaseView):

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.columns['BatchID']['title'] = _('Case ID')
        # Add Client Patient fields
        self.columns['getPatientID'] = {
            'title': _('Patient ID'),
        }
        self.columns['getClientPatientID'] = {
            'title': _("Client PID"),
            'sortable': False,
        }
        self.columns['getPatientTitle'] = {
            'title': _('Patient'),
        }
        self.columns['getDoctorTitle'] = {
            'title': _('Doctor'),
        }

    def folderitems(self, full_objects=False):
        logger.info("*** Bika Health's folderitems ***")
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
            self.remove_column('getPatientTitle')
            self.remove_column('getDoctorTitle')
        # Otherwise show the columns in the list
        else:
            for rs in self.review_states:
                i = rs['columns'].index('BatchID') + 1
                rs['columns'].insert(i, 'getClientPatientID')
                rs['columns'].insert(i, 'getPatientID')
                rs['columns'].insert(i, 'getPatientTitle')
                rs['columns'].insert(i, 'getDoctorTitle')
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

        item['getPatientID'] = obj.getPatientID
        item['getPatientTitle'] = obj.getPatientTitle
        item['getClientPatientID'] = obj.getClientPatientID
        url = '{}/analysisrequests'.format(obj.getPatientURL)
        item['replace']['getPatientTitle'] = get_link(url, obj.getPatientTitle)
        item['replace']['getPatientID'] = get_link(url, obj.getPatientID)
        item['replace']['getClientPatientID'] = get_link(url, obj.getClientPatientID)

        item['getDoctorTitle'] = obj.getDoctorTitle
        if obj.getDoctorURL:
            url = '{}/analysisrequests'.format(obj.getDoctorURL)
            item['replace']['getDoctorTitle'] = get_link(url, obj.getDoctorTitle)
        return item
