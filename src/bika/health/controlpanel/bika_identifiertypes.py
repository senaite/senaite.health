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

from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi

from bika.lims import api
from bika.lims.browser.bika_listing import BikaListingView
from bika.health.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.health.interfaces import IIdentifierTypes
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

from bika.lims.utils import get_link


class IdentifierTypesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(IdentifierTypesView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'IdentifierType',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=IdentifierType',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Identifier Types"))
        self.icon = self.portal_url + "/++resource++bika.health.images/identifiertype_big.png"
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Title'),
                      'index':'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'is_active': True},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Description']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'is_active': False},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Description']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Description']},
        ]

    def before_render(self):
        """Before template render hook
        """
        super(IdentifierTypesView, self).before_render()
        # Don't allow any context actions on Identifier types folder
        self.request.set("disable_border", 1)

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        item["Description"] = obj.Description()
        item["replace"]["Title"] = get_link(item["url"], item["Title"])
        return item


schema = ATFolderSchema.copy()
class IdentifierTypes(ATFolder):
    implements(IIdentifierTypes)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(IdentifierTypes, PROJECTNAME)
