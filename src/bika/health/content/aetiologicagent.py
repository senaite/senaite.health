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
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.health.config import PROJECTNAME
from Products.Archetypes.public import *
from Products.ATExtensions.ateapi import RecordsField
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    RecordsField('AetiologicAgentSubtypes',
        type='aetiologicagentsubtypes',
        subfields=('Subtype', 'SubtypeRemarks'),
        subfield_labels={'Subtype':_('Subtype'),
                         'SubtypeRemarks':_('Remarks')},
        subfield_sizes={'Subtype':10,
                        'SubtypeRemarks':25},
        widget=RecordsWidget(
                label='Subtypes',
                description=_("A list of aetiologic agent subtypes."),
                visible = True,
        ),
    ),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class AetiologicAgent(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(AetiologicAgent, PROJECTNAME)
