# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.interface import implements
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseContent
from bika.health.interfaces import IEthnicity
from bika.lims.content.bikaschema import BikaSchema
from bika.health import config


schema = BikaSchema.copy() + atapi.Schema((

))

schema['description'].widget.visible = True
schema['description'].schemata = 'default'


class Ethnicity(BaseContent):
    # It implements the IEthnicity interface
    implements(IEthnicity)
    schema = schema

# Activating the content type in Archetypes' internal types registry
atapi.registerType(Ethnicity, config.PROJECTNAME)
