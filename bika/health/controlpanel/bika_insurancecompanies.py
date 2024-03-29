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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from zope.interface.declarations import implements

from bika.health import bikaMessageFactory as _
from bika.health.config import PROJECTNAME
from bika.health.interfaces import IInsuranceCompanies
from bika.lims import api
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import get_link


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
             'contentFilter': {'is_active': True},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Name',
                         'EmailAddress',
                         'Phone',
                         'Fax',
                         'Description']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'is_active': False},
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

    def before_render(self):
        """Before template render hook
        """
        super(InsuranceCompaniesView, self).before_render()
        # Don't allow any context actions on Insurance Companies folder
        self.request.set("disable_border", 1)

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        item["Description"] = obj.Description()
        item["replace"]["Name"] = get_link(item["url"], item["Name"])
        return item


schema = ATFolderSchema.copy()
class InsuranceCompanies(ATFolder):
    implements(IInsuranceCompanies)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(InsuranceCompanies, PROJECTNAME)
