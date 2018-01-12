# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import DateTimeField
from Products.Archetypes.public import registerType
from Products.Archetypes.public import Schema
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.health.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    DateTimeField('StartDate',
        schemata = 'default',
        required = True,
        widget = DateTimeWidget(
            label = _("Epidemiological year start date"),
        ),
    ),
    DateTimeField('EndDate',
        schemata = 'default',
        required = True,
        widget = DateTimeWidget(
            label = _("Epidemiological year end date"),
        ),
    ),
))

schema['description'].widget.visible = False
schema['description'].schemata = 'default'

class EpidemiologicalYear(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(EpidemiologicalYear, PROJECTNAME)
