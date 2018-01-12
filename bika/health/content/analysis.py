# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
