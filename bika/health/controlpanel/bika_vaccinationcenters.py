# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.health.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.health.interfaces import IVaccinationCenters
from bika.lims.interfaces import IHaveNoBreadCrumbs
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

class VaccinationCentersView(BikaListingView):
    implements(IFolderContentsView, IViewView)
    def __init__(self, context, request):
        super(VaccinationCentersView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'VaccinationCenter',
                              'sort_on': 'getName'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=VaccinationCenter',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Vaccination Centers"))
        self.icon = self.portal_url + "/++resource++bika.health.images/vaccinationcenter_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.columns = {
            'Name': {'title': _('Name'),
                     'index': 'getName'},
            'Email': {'title': _('Email'),
                      'toggle': True},
            'Phone': {'title': _('Phone'),
                      'toggle': True},
            'Fax': {'title': _('Fax'),
                    'toggle': True},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Name',
                         'Email',
                         'Phone',
                         'Fax']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Name',
                         'Email',
                         'Phone',
                         'Fax']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Name',
                         'Email',
                         'Phone',
                         'Fax']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Name'] = obj.getName()
            items[x]['Email'] = obj.getEmailAddress()
            items[x]['Phone'] = obj.getPhone()
            items[x]['Fax'] = obj.getFax()
            items[x]['replace']['Name'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Name'])

        return items

schema = ATFolderSchema.copy()
class VaccinationCenters(ATFolder):
    implements(IVaccinationCenters)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(VaccinationCenters, PROJECTNAME)
