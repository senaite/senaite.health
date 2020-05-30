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

import json

from Products.ATContentTypes.content import schemata
from Products.Archetypes.public import registerType
from Products.Archetypes.utils import DisplayList
from Products.CMFCore.utils import getToolByName
from bika.health.config import PROJECTNAME
from bika.health.interfaces import IDoctors
from bika.lims import api
from bika.lims.interfaces import IHaveNoBreadCrumbs
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

schema = ATFolderSchema.copy()


class Doctors(ATFolder):
    """Root folder for Doctors
    """
    implements(IDoctors, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema

    def getContacts(self, dl=True):
        pc = getToolByName(self, 'portal_catalog')
        bsc = getToolByName(self, 'bika_setup_catalog')
        pairs = []
        objects = []
        # All Doctors
        for contact in pc(portal_type='Doctor',
                          is_active=True,
                          sort_on='sortable_title'):
            pairs.append((contact.UID, contact.Title))
            if not dl:
                objects.append(contact.getObject())
        # All LabContacts
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

registerType(Doctors, PROJECTNAME)
