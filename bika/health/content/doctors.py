# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from Products.Archetypes.utils import DisplayList
from bika.health.config import PROJECTNAME
from bika.health.interfaces import IDoctors
from plone.app.layout.globals.interfaces import IViewView
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.health.permissions import *
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
import json

schema = ATFolderSchema.copy()


class Doctors(ATFolder):
    implements(IDoctors)
    displayContentsTab = False
    schema = schema

    def getContacts(self, dl=True):
        pc = getToolByName(self, 'portal_catalog')
        bsc = getToolByName(self, 'bika_setup_catalog')
        pairs = []
        objects = []
        # All Doctors
        for contact in pc(portal_type='Doctor',
                          inactive_state='active',
                          sort_on='sortable_title'):
            pairs.append((contact.UID, contact.Title))
            if not dl:
                objects.append(contact.getObject())
        # All LabContacts
        for contact in bsc(portal_type='LabContact',
                           inactive_state='active',
                           sort_on='sortable_title'):
            pairs.append((contact.UID, contact.Title))
            if not dl:
                objects.append(contact.getObject())
        return dl and DisplayList(pairs) or objects

    def getCCs(self):
        """Return a JSON value, containing all Contacts and their default CCs.
           This function is used to set form values for javascript.
        """
        items = []
        for contact in self.getContacts(dl=False):
            item = {'uid': contact.UID(), 'title': contact.Title()}
            ccs = []
            if hasattr(contact, 'getCCContact'):
                for cc in contact.getCCContact():
                    if isActive(cc):
                        ccs.append({'title': cc.Title(),
                                    'uid': cc.UID(), })
            item['ccs_json'] = json.dumps(ccs)
            item['ccs'] = ccs
            items.append(item)
        items.sort(lambda x, y: cmp(x['title'].lower(), y['title'].lower()))
        return items

# schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(Doctors, PROJECTNAME)
