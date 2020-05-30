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
from bika.lims.config import PROJECTNAME as BIKALIMS_PROJECTNAME
from bika.lims.content.analysis import Analysis as BaseAnalysis
from archetypes.schemaextender.interfaces import ISchemaExtender
from bika.lims.interfaces import IAnalysis
from zope.component import adapts
from zope.interface import implements


class AnalysisSchemaExtender(object):
    adapts(IAnalysis)
    implements(ISchemaExtender)

    fields = []

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


class Analysis(BaseAnalysis):
    """ Inherits from bika.lims.content.Analysis
    """


# overrides bika.lims.content.Analysis
atapi.registerType(Analysis, BIKALIMS_PROJECTNAME)
