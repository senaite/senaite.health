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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from bika.health import bikaMessageFactory as _
from bika.health.config import PROJECTNAME
from bika.health.interfaces import IInsuranceCompany
from bika.lims.browser.fields.remarksfield import RemarksField
from bika.lims.browser.widgets.remarkswidget import RemarksWidget
from bika.lims.content.organisation import Organisation
from zope.interface import implements

schema = Organisation.schema.copy() + ManagedSchema((
    RemarksField(
        'Remarks',
        searchable = True,
        widget = RemarksWidget(
            label = _('Remarks'),
        ),
    ),
))

class InsuranceCompany(Organisation):
    implements(IInsuranceCompany)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(InsuranceCompany, PROJECTNAME)
