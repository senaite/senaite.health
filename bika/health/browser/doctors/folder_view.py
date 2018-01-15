# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.lims.browser.client import ClientContactsView
from bika.health.permissions import *


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
        if mtool.checkPermission(AddDoctor, self.context):
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=Doctor',
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
