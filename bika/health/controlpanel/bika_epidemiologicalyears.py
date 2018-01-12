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
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.health.interfaces import IEpidemiologicalYears
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

class EpidemiologicalYearsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(EpidemiologicalYearsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'EpidemiologicalYear',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=EpidemiologicalYear',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Epidemiological Years"))
        self.icon = self.portal_url + "/++resource++bika.health.images/epidemiologicalyear_big.png"
        self.description = _("Epidemiological year calendars")
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Title'),
                     'index':'sortable_title'},

            'getStartDate': {'title':_('Start Date'),
                             'index':'getStartDate'},

            'getEndDate': {'title':_('End Date'),
                           'index': 'getEndDate'},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'getStartDate',
                         'getEndDate']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'getStartDate',
                         'getEndDate']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'getStartDate',
                         'getEndDate']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
            items[x]['getStartDate'] = self.ulocalized_time(obj.getStartDate())
            items[x]['getEndDate'] = self.ulocalized_time(obj.getEndDate())

        return items

schema = ATFolderSchema.copy()
class EpidemiologicalYears(ATFolder):
    implements(IEpidemiologicalYears)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(EpidemiologicalYears, PROJECTNAME)
