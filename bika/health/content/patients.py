# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.health.config import PROJECTNAME
from bika.health.interfaces import IPatients
from bika.health.permissions import *
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
import json

schema = ATFolderSchema.copy()


class Patients(ATFolder):
    implements(IPatients)
    displayContentsTab = False
    schema = schema

    def getContacts(self, dl=True):
        bsc = getToolByName(self, 'bika_setup_catalog')
        pairs = []
        objects = []
        client = hasattr(self, 'getPrimaryReferrer') and self.getPrimaryReferrer() or None
        if client:
            for contact in client.objectValues('Contact'):
                if isActive(contact):
                    pairs.append((contact.UID(), contact.Title()))
                    if not dl:
                        objects.append(contact)
            pairs.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
            return dl and DisplayList(pairs) or objects
        # fallback - all Lab Contacts
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
atapi.registerType(Patients, PROJECTNAME)
