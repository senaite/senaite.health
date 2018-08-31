# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from collections import OrderedDict

from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.health.permissions import *
from bika.lims import api
from bika.lims.browser.client import ClientContactsView
from bika.lims.interfaces import IClient
from bika.lims.utils import get_link
from plone.memoize import view as viewcache


class DoctorsView(ClientContactsView):

    def __init__(self, context, request):
        super(DoctorsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Doctor',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.title = self.context.translate(_("Doctors"))
        self.icon = self.portal_url + "/++resource++bika.health.images/doctor_big.png"
        self.description = ""

        self.columns = OrderedDict((
            ("getDoctorID", {
                "title": _('Doctor ID'),
                "index": "getDoctorID",
                "sortable": True, }),
            ("getFullname", {
                "title": _("Full Name"),
                "index": "getFullname",
                "sortable": True, }),
            ("getPrimaryReferrer", {
                "title": _("Primary Referrer"),
                "index": "getPrimaryReferrerUID",
                "sortable": True, }),
            ("Username", {
                "title": _("User Name"), }),
            ("getEmailAddress", {
                "title": _("Email Address"), }),
            ("getBusinessPhone", {
                "title": _("Business Phone"), }),
            ("getMobilePhone", {
                "title": _("MobilePhone"), }),
        ))

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [],
             'columns': self.columns.keys()},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        can_add_doctors = mtool.checkPermission(AddDoctor, self.context)
        if can_add_doctors:
            add_doctors_url = '{}/doctors/createObject?type_name=Doctor' \
                .format(self.portal_url)
            self.context_actions[_('Add')] = {
                'url': add_doctors_url,
                'icon': '++resource++bika.lims.images/add.png'
            }
        if mtool.checkPermission(ManageDoctors, self.context):
            self.review_states[0]['transitions'].append({'id':'deactivate'})
            self.review_states.append(
                {'id':'inactive',
                 'title': _('Dormant'),
                 'contentFilter': {'inactive_state': 'inactive'},
                 'transitions': [{'id':'activate'}, ],
                 'columns': self.columns.keys()})
            self.review_states.append(
                {'id':'all',
                 'title': _('All'),
                 'contentFilter':{},
                 'transitions':[{'id':'empty'}],
                 'columns': self.columns.keys()})
            stat = self.request.get("%s_review_state"%self.form_id, 'default')
            self.show_select_column = stat != 'all'

        # If the current context is a Client, filter Doctors by Client UID
        if IClient.providedBy(self.context):
            client_uid = api.get_uid(self.context)
            self.contentFilter['getPrimaryReferrerUID'] = client_uid

        # If the current user is a client contact, do not display the doctors
        # assigned to other clients
        elif self.get_user_client_uid():
            client_uid = self.get_user_client_uid()
            self.contentFilter['getPrimaryReferrerUID'] = [client_uid, None]

        return super(DoctorsView, self).__call__()

    @viewcache.memoize
    def get_user_client_uid(self, default=None):
        """Returns the id of the client the current user belongs to
        """
        client = api.get_current_client()
        if client:
            return api.get_uid(client)
        return default

    def folderitem(self, obj, item, index):
        """Applies new properties to the item to be rendered
        """
        item = super(DoctorsView, self).folderitem(obj, item, index)
        url = item.get("url")
        doctor_id = item.get("getDoctorID")
        item['replace']['getDoctorID'] = get_link(url, value=doctor_id)
        item['getPrimaryReferrer'] = ""
        doctor = api.get_object(obj)
        pri = doctor.getPrimaryReferrer()
        if pri:
            pri_url = pri.absolute_url()
            pri = pri.Title()
            item['replace']['getPrimaryReferrer'] = get_link(pri_url, value=pri)
        return item
