# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.browser.bika_listing import BikaListingView
from bika.health.config import PROJECTNAME
from bika.health import bikaMessageFactory as _
from bika.health.interfaces import IInsuranceCompanies
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

class InsuranceCompaniesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(InsuranceCompaniesView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'InsuranceCompany',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=InsuranceCompany',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Insurance Companies"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/laboratory_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Name': {'title': _('Company Name'),
                      'index':'sortable_title'},
            'EmailAddress': {'title': _('Email'),
                      'toggle': True},
            'Phone': {'title': _('Phone'),
                      'toggle': True},
            'Fax': {'title': _('Fax'),
                    'toggle': False},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': False},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Name',
                         'EmailAddress',
                         'Phone',
                         'Fax',
                         'Description']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Name',
                         'EmailAddress',
                         'Phone',
                         'Fax',
                         'Description']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Name',
                         'EmailAddress',
                         'Phone',
                         'Fax',
                         'Description']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Description'] = obj.Description()
            items[x]['replace']['Name'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Name'])

        return items

schema = ATFolderSchema.copy()
class InsuranceCompanies(ATFolder):
    implements(IInsuranceCompanies)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(InsuranceCompanies, PROJECTNAME)
