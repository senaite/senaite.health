# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from bika.health import bikaMessageFactory as _
from bika.health.config import PROJECTNAME
from bika.lims.content.organisation import Organisation
from bika.health.interfaces import IInsuranceCompany
from zope.interface import implements

schema = Organisation.schema.copy() + ManagedSchema((
    TextField('Remarks',
        searchable = True,
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type = "text/html",
        widget = TextAreaWidget(
            macro = "bika_widgets/remarks",
            label = _('Remarks'),
            append_only = True,
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
