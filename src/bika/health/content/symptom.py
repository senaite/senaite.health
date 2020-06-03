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

from AccessControl import ClassSecurityInfo
from bika.health import bikaMessageFactory as _
from bika.health.config import GENDERS_APPLY
from bika.health.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import StringField
from Products.Archetypes.public import registerType

schema = BikaSchema.copy() + Schema((

    StringField("Code"),

    StringField(
        "Gender",
        vocabulary=GENDERS_APPLY,
        index="FieldIndex",
        widget=SelectionWidget(
            format="select",
            label=_("Applies to"),
        ),
    ),

    BooleanField(
        "SeverityAllowed",
        default=False,
        widget=BooleanWidget(
            label=_("Severity levels permitted"),
            description=_(
                "Check if patient can experience different stress "
                "levels (none, mild, moderate, severe) of the symptom"),
        ),
    ),
))

schema["description"].widget.visible = True
schema["description"].schemata = "default"

schema.moveField("Code", before="title")


class Symptom(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(Symptom, PROJECTNAME)
