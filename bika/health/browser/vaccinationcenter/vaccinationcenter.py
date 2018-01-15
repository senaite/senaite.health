# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _

class ContactsView(BikaListingView):

    def __init__(self, context, request):
        super(ContactsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'VaccinationCenterContact',
            'sort_on':'sortable_title',
            'path': {
                "query": "/".join(context.getPhysicalPath()),
                "level" : 0
            }
        }
        self.context_actions = {_('Add'):
            {'url': 'createObject?type_name=VaccinationCenterContact',
             'icon': '++resource++bika.lims.images/add.png'}
        }
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.icon = self.portal_url + "/++resource++bika.health.images/vaccinationcenter_contact_big.png"
        self.title = _b("Contacts")

        self.columns = {
            'getFullname': {'title': _('Full Name')},
            'getEmailAddress': {'title': _('Email Address')},
            'getBusinessPhone': {'title': _('Business Phone')},
            'getMobilePhone': {'title': _('Mobile Phone')},
            'getFax': {'title': _('Fax')},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['getFullname',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone',
                         'getFax']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['getFullname',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone',
                         'getFax']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['getFullname',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone',
                         'getFax']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue

            items[x]['replace']['getFullName'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['obj'].getFullname())

            items[x]['replace']['getEmailAddress'] = "<a href='mailto:%s'>%s</a>" % \
                 (items[x]['getEmailAddress'], items[x]['obj'].getEmailAddress())

        return items
