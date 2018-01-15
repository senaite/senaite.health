# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from bika.health.config import PROJECTNAME
from bika.lims.browser.widgets import RecordsWidget
from zope.interface import implements

schema = BikaSchema.copy() + Schema((

    StringField('Form',
        vocabulary = "getImmunizationFormsList",
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Immunization form",
                      "Type"),
            description = _("Select a type of immunization. <br/>"
                      "Active immunization entails the introduction of a foreign molecule "
                      "into the body, which causes the body itself to generate immunity "
                      "against the target. Vaccination is an active form of immunization<br/>"
                      "Passive immunization is where pre-synthesized elements of the immune "
                      "system are transferred to a person so that the body does not need to "
                      "produce these elements itself. Currently, antibodies can be used for "
                      "passive immunization"),
        ),
    ),

    TextField('RelevantFacts',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Relevant Facts"),
        ),
    ),

    TextField('GeographicalDistribution',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Geographical distribution"),
            description = _("Geographical areas can be characterized as having high, intermediate "
                            "or low levels of infection.")
        ),
    ),

    TextField('Transmission',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Transmission"),
        ),
    ),

    TextField('Symptoms',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Symptoms"),
        ),
    ),

    TextField('Risk',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Collectives at risk"),
        ),
    ),

    TextField('Treatment',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Treatment"),
        ),
    ),

    TextField('Prevention',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Prevention"),
        ),
    ),

))

schema['description'].widget.visible = True
schema['description'].schemata = 'default'

def getImmunizationForms(context):
    """ Return the current list of immunization forms
    """
    # Active immunization entails the introduction of a foreign molecule into the body,
    # which causes the body itself to generate immunity against the target. Vaccination
    # is an active form of immunization.
    # Passive immunization is where pre-synthesized elements of the immune system are
    # transferred to a person so that the body does not need to produce these elements
    # itself. Currently, antibodies can be used for passive immunization.
    types = [
             ('active', context.translate(_('Active immunization'))),
             ('passive', context.translate(_('Passive immunization'))),
             ]
    return DisplayList(types)

class Immunization(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getImmunizationFormsList(self):
        return getImmunizationForms(self)

registerType(Immunization, PROJECTNAME)
