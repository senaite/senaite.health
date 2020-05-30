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

from Products.Archetypes import atapi
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from zope.interface.declarations import implements

from bika.health.config import PROJECTNAME
from bika.health.interfaces import IPatients
from bika.lims.interfaces import IHaveNoBreadCrumbs

schema = ATFolderSchema.copy()


class Patients(ATFolder):
    implements(IPatients, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema

atapi.registerType(Patients, PROJECTNAME)
