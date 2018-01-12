# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.health import bikaMessageFactory as _
from bika.health.widgets.analysisspecificationwidget import \
    AnalysisSpecificationWidget, AnalysisSpecificationPanicValidator
from bika.lims.config import PROJECTNAME as BIKALIMS_PROJECTNAME
from bika.lims.content.analysisspec import AnalysisSpec as BaseAnalysisSpec
from bika.lims.interfaces import IAnalysisSpec
from zope.component import adapts
from zope.interface import implements


class AnalysisSpecSchemaModifier(object):
    adapts(IAnalysisSpec)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):

        # Add panic alert range columns
        validator = AnalysisSpecificationPanicValidator()
        schema['ResultsRange'].subfields += ('minpanic', 'maxpanic')
        schema['ResultsRange'].subfield_validators['minpanic'] = validator
        schema['ResultsRange'].subfield_validators['maxpanic'] = validator
        schema['ResultsRange'].subfield_labels['minpanic'] = _('Min panic')
        schema['ResultsRange'].subfield_labels['maxpanic'] = _('Max panic')
        srcwidget = schema['ResultsRange'].widget
        schema['ResultsRange'].widget = AnalysisSpecificationWidget(
                    checkbox_bound=srcwidget.checkbox_bound,
                    label=srcwidget.label,
                    description=srcwidget.description,
        )
        return schema


class AnalysisSpec(BaseAnalysisSpec):
    """ Inherits from bika.content.analysisspec.AnalysisSpec
    """
    pass

atapi.registerType(AnalysisSpec, BIKALIMS_PROJECTNAME)
