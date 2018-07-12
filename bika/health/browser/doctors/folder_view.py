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
        self._apply_filter_by_client()
        return super(DoctorsView, self).__call__()

    def folderitems(self):
        items = super(DoctorsView, self).folderitems()
        for x in range(len(items)):
            if not 'obj' in items[x]:
                continue
            obj = items[x]['obj']
            items[x]['replace']['getDoctorID'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getDoctorID'])
            items[x]['replace']['getFullname'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getFullname'])

        return items

    def _apply_filter_by_client(self):
        """
        From the current user and the context, update the filter that will be
        used for filtering the Doctor's list.
        """
        # If the current context is a Client, filter Doctors by Client UID
        if IClient.providedBy(self.context):
            client_uid = api.get_uid(self.context)
            self.contentFilter['getPrimaryReferrerUID'] = client_uid
            return

        # If the current user is a Client contact, filter the Doctors in
        # accordance. For the rest of users (LabContacts), the visibility of
        # the doctors depend on their permissions
        user = api.get_current_user()
        roles = user.getRoles()
        if 'Client' not in roles:
            return

        # Are we sure this a ClientContact?
        # May happen that this is a Plone member, w/o having a ClientContact
        # assigned or having a LabContact assigned... weird
        contact = api.get_user_contact(user)
        if not contact or ILabContact.providedBy(contact):
            return

        # Is the parent from the Contact a Client?
        client = api.get_parent(contact)
        if not client or not IClient.providedBy(client):
            return
        client_uid = api.get_uid(client)
        self.contentFilter['getPrimaryReferrerUID'] = client_uid
