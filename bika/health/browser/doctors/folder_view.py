# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName

from bika.health import bikaMessageFactory as _
from bika.health.permissions import *
from bika.lims import api
from bika.lims.browser.client import ClientContactsView
from bika.lims.interfaces import IClient, ILabContact
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
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50

        self.columns = {
            'getDoctorID': {'title': _('Doctor ID'),
                            'index': 'getDoctorID'},
            'getFullname': {'title': _('Full Name'),
                            'index': 'getFullname'},
            'getEmailAddress': {'title': _('Email Address')},
            'getBusinessPhone': {'title': _('Business Phone')},
            'getMobilePhone': {'title': _('Mobile Phone')},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [],
             'columns': ['getDoctorID',
                         'getFullname',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone']},
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
                 'columns': ['getDoctorID',
                             'getFullname',
                             'getEmailAddress',
                             'getBusinessPhone',
                             'getMobilePhone']})
            self.review_states.append(
                {'id':'all',
                 'title': _('All'),
                 'contentFilter':{},
                 'transitions':[{'id':'empty'}],
                 'columns': ['getDoctorID',
                             'getFullname',
                             'getEmailAddress',
                             'getBusinessPhone',
                             'getMobilePhone']})
            stat = self.request.get("%s_review_state"%self.form_id, 'default')
            self.show_select_column = stat != 'all'

        # If the current context is a Client, filter Doctors by Client UID
        if IClient.providedBy(self.context):
            client_uid = api.get_uid(self.context)
            self.contentFilter['getPrimaryReferrerUID'] = client_uid

        return super(DoctorsView, self).__call__()

    @viewcache.memoize
    def get_user_client_uid(self, default=None):
        """Returns the id of the client the current user belongs to
        """
        user = api.get_current_user()
        roles = user.getRoles()
        if 'Client' not in roles:
            return default

        contact = api.get_user_contact(user)
        if not contact or ILabContact.providedBy(contact):
            return default

        client = api.get_parent(contact)
        if not client or not IClient.providedBy(client):
            return default

        return api.get_uid(client)

    def isItemAllowed(self, obj):
        """
        It checks if the item can be added to the list. If the current user is
        a client contact, only doctors without client assigned or assigned to
        sime client as the contact will be displayed.
        """
        allowed = super(DoctorsView, self).isItemAllowed(obj)
        if not allowed:
            return False

        # Current user belongs to a client
        client_uid = self.get_user_client_uid()
        if not client_uid:
            return True

        # Only visible if the Doctor has the same client assigned or None
        referrer_uid = api.get_object(obj).getPrimaryReferrerUID()
        return not referrer_uid or referrer_uid == client_uid


    def folderitem(self, obj, item, index):
        """Applies new properties to the item to be rendered
        """
        item = super(DoctorsView, self).folderitem(obj, item, index)
        url = item.get("url")
        doctor_id = item.get("getDoctorID")
        item['replace']['getDoctorID'] = get_link(url, value=doctor_id)
        return item
