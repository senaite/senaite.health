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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

import json

from Products.Archetypes import atapi
from Products.Archetypes import DisplayList
from Products.CMFCore.utils import getToolByName
from bika.health.config import PROJECTNAME
from bika.health.interfaces import IPatients
from bika.lims import api
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

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
                if api.is_active(contact):
                    pairs.append((contact.UID(), contact.Title()))
                    if not dl:
                        objects.append(contact)
            pairs.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
            return dl and DisplayList(pairs) or objects
        # fallback - all Lab Contacts
        for contact in bsc(portal_type='LabContact',
                           is_active=True,
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
                    if api.is_active(cc):
                        ccs.append({'title': cc.Title(),
                                    'uid': cc.UID(), })
            item['ccs_json'] = json.dumps(ccs)
            item['ccs'] = ccs
            items.append(item)
        items.sort(lambda x, y: cmp(x['title'].lower(), y['title'].lower()))
        return items

# schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(Patients, PROJECTNAME)
