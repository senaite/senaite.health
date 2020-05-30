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

""" http://pypi.python.org/pypi/archetypes.schemaextender
"""
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from bika.health import bikaMessageFactory as _
from bika.lims.fields import *
from bika.lims.interfaces import IClient
from zope.component import adapts
from zope.interface import implements


class ClientSchemaExtender(object):
    adapts(IClient)
    implements(IOrderableSchemaExtender)

    fields = [
        ExtBooleanField('DefaultResultsDistributionToPatients',
            schemata="Results Reports",
            default=True,
            widget=BooleanWidget(
                label=_("Inherit default settings for Patient results distribution"),
                description=_("If checked, the settings for results reports "
                              "distribution to patients will be inherited "
                              "from Bika Setup, so further changes in Bika "
                              "Setup for this setting will be populated too."))
        ),
        ExtBooleanField('AllowResultsDistributionToPatients',
            schemata="Results Reports",
            default=False,
            widget=BooleanWidget(
                label=_("Allow results distribution to Patients"),
                description=_("If checked, results reports will also be sent "
                              "to the Patient automatically. This setting can "
                              "be overriden either on Patient's 'Publication "
                              "preferences' tab."))
        ),
        ExtLinesField('PatientPublicationPreferences',
            vocabulary_factory='bika.health.obsolete.CustomPubPrefVocabularyFactory',
            schemata='Results Reports',
            widget=MultiSelectionWidget(
                label=_("Default publication preference for Patients"),
                description=_("Select the preferred channels to be used for "
                              "sending the results reports to Patients. "
                              "This setting can be overriden on Patient's "
                              "'Publication preferences' tab.")
                )
        ),
        ExtBooleanField('PatientPublicationAttachmentsPermitted',
            default=False,
            schemata='Results Reports',
            widget=BooleanWidget(
                label=_("Results attachments permitted"),
                description=_("File attachments to results, e.g. microscope "
                              "photos, will be included in emails to patients "
                              "if this option is enabled. This setting can be "
                              "overriden on Patient's 'Publication "
                              "preferences' tab.")
                )
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, schematas):
        sch = schematas['Results Reports']
        sch.remove('AllowResultsDistributionToPatients')
        sch.insert(sch.index('PatientPublicationPreferences'), 'AllowResultsDistributionToPatients')
        schematas['Results Reports'] = sch
        return schematas
