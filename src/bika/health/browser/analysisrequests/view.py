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

    def folderitems(self):
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
        return super(AnalysisRequestsView, self).folderitems()

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
        item = super(AnalysisRequestsView, self).folderitem(obj, item, index)

        url = '{}/analysisrequests'.format(obj.getPatientURL)
        item['getPatientID'] = obj.getPatientID
        item['getPatientTitle'] = obj.getPatientTitle
        item['getClientPatientID'] = obj.getClientPatientID

        # Replace with Patient's URLs
        if obj.getClientPatientID:
            item['replace']['getClientPatientID'] = get_link(
                url, obj.getClientPatientID)

        if obj.getPatientTitle:
            item['replace']['getPatientTitle'] = get_link(
                url, obj.getPatientTitle)

        if obj.getPatientID:
            item['replace']['getPatientID'] = get_link(url, obj.getPatientID)

        # Doctor
        item['getDoctorTitle'] = obj.getDoctorTitle
        if obj.getDoctorURL:
            url = '{}/analysisrequests'.format(obj.getDoctorURL)
            item['replace']['getDoctorTitle'] = get_link(url, obj.getDoctorTitle)

        return item
