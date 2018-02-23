# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

""" http://pypi.python.org/pypi/archetypes.schemaextender
"""
from Products.Archetypes.public import *
from bika.lims.fields import *
from bika.lims.interfaces import IClient
from bika.health.widgets import *
from plone.indexer.decorator import indexer
from bika.health import bikaMessageFactory as _
from zope.component import adapts, getAdapters
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from bika.lims.vocabularies import CustomPubPrefVocabularyFactory

@indexer(IClient)
def getClientID(instance):
    return instance.Schema()['ClientID'].get(instance)


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
            vocabulary_factory='bika.lims.vocabularies.CustomPubPrefVocabularyFactory',
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
