# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from bika.health.config import PROJECTNAME, GENDERS_APPLY
from bika.lims.browser.widgets import RecordsWidget
from zope.interface import implements

schema = BikaSchema.copy() + Schema((

    StringField('Code'),

    StringField('Gender',
            vocabulary=GENDERS_APPLY,
            index='FieldIndex',
            widget=SelectionWidget(
                format='select',
                label=_('Applies to'),
            ),
    ),

    BooleanField('SeverityAllowed',
           default=False,
           widget=BooleanWidget(
               label=_("Severity levels permitted"),
               description=_("Check if patient can experience different stress  levels (none, mild, moderate, severe) of the symptom"),
           ),
    ),
))

schema['description'].widget.visible = True
schema['description'].schemata = 'default'

schema.moveField('Code', before='title')

class Symptom(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(Symptom, PROJECTNAME)
