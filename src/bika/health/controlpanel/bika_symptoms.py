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

from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from zope.interface.declarations import implements

from bika.health import bikaMessageFactory as _
from bika.health.config import GENDERS_APPLY
from bika.health.config import PROJECTNAME
from bika.health.interfaces import ISymptoms
from bika.lims import api
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import get_link


class SymptomsView(BikaListingView):
    implements(IFolderContentsView,IViewView)

    def __init__(self,context,request):
        super(SymptomsView,self).__init__(context,request)
        self.catalog='bika_setup_catalog'
        self.contentFilter={'portal_type': 'Symptom',
                              'sort_on': 'sortable_title'}
        self.context_actions={_('Add'):
                                {'url': 'createObject?type_name=Symptom',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title=self.context.translate(_("Symptoms"))
        self.icon = self.portal_url + "/++resource++bika.health.images/symptom_big.png"
        self.description=_("Additional Symptoms not covered by ICD codes, can be entered here.")
        self.show_sort_column=False
        self.show_select_row=False
        self.show_select_column=True
        self.pagesize=25

        self.columns={
            'Title': {'title': _('Symptom'),
                      'index':'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
            'Gender': {'title': _('Gender'),
                            'index': 'getGender',
                            'toggle': True},
        }

        self.review_states=[
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'is_active': True},
             'transitions': [{'id':'deactivate'},],
             'columns': ['Title',
                         'Description',
                         'Gender']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'is_active': False},
             'transitions': [{'id':'activate'},],
             'columns': ['Title',
                         'Description',
                         'Gender']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Description',
                         'Gender']},
        ]

    def before_render(self):
        """Before template render hook
        """
        super(SymptomsView, self).before_render()
        # Don't allow any context actions on Symptoms folder
        self.request.set("disable_border", 1)

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        item["Description"] = obj.Description()
        item["Gender"] = GENDERS_APPLY.getValue(obj.getGender())
        item["replace"]["Title"] = get_link(item["url"], item["Title"])
        return item


schema=ATFolderSchema.copy()
class Symptoms(ATFolder):
    implements(ISymptoms)
    displayContentsTab=False
    schema=schema

schemata.finalizeATCTSchema(schema,folderish=True,moveDiscussion=False)
atapi.registerType(Symptoms,PROJECTNAME)
