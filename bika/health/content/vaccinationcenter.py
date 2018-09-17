# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.Archetypes.utils import DisplayList
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.health.config import PROJECTNAME
from bika.lims.browser.fields.remarksfield import RemarksField
from bika.lims.browser.widgets.remarkswidget import RemarksWidget
from bika.lims.content.organisation import Organisation
from bika.health.interfaces import IVaccinationCenter
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

#schema['AccountNumber'].write_permission = ManageReferenceSuppliers

class VaccinationCenter(Organisation):
    implements(IVaccinationCenter)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(VaccinationCenter, PROJECTNAME)
