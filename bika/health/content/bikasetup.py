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

from Products.Archetypes.Widget import BooleanWidget
from archetypes.schemaextender.interfaces import ISchemaExtender,\
    IOrderableSchemaExtender
from bika.lims.fields import *
from bika.health import bikaMessageFactory as _
from bika.lims.interfaces import IBikaSetup
from zope.component import adapts, getAdapters
from zope.interface import implements


class BikaSetupSchemaExtender(object):
    adapts(IBikaSetup)
    implements(IOrderableSchemaExtender)

    fields = [
        ExtBooleanField('EnablePanicAlert',
            schemata="Analyses",
            default=False,
            widget=BooleanWidget(
                label=_("Enable panic levels alert"),
                description=_("Alert labmanagers with an email when an "
                              "analysis result exceeding a panic level is "
                              "submitted"))
        ),
        ExtBooleanField('AutoShowPanicAlertEmailPopup',
            schemata="Analyses",
            default=False,
            widget=BooleanWidget(
                label=_("Show client email pop-up when panic level"),
                description=_("If enabled, shows automatically an email form "
                              "pop-up for alerting the client about a panic "
                              "level exceeded when Analysis Request view is "
                              "loaded"))
        ),
        ExtStringField('PatientConditionsHeightUnits',
            schemata="Cases",
            default=_("Feet/inches"),
            widget=StringWidget(
                label=_("Patient condition height units"),
                description=_("Use '/' symbol to allow multiple-units submission")
            )
        ),
        ExtStringField('PatientConditionsWeightUnits',
            schemata="Cases",
            default=_("Lbs"),
            widget=StringWidget(
                label=_("Patient condition weight units"),
                description=_("Use '/' symbol to allow multiple-units submission")
            )
        ),
        ExtStringField('PatientConditionsWaistUnits',
            schemata="Cases",
            default=_("Inches"),
            widget=StringWidget(
                label=_("Patient condition waist units"),
                description=_("Use '/' symbol to allow multiple-units submission")
            )
        ),
        ExtBooleanField('AllowResultsDistributionToPatients',
            schemata="Results Reports",
            default=False,
            widget=BooleanWidget(
                label=_("Allow results distribution to Patients"),
                description=_("If checked, results reports will also be sent "
                              "to the Patient automatically. This setting can "
                              "be overriden either on 'Patient publication "
                              "preferences' tab from Client view or on "
                              "Patient's 'Publication preferences' tab."))
        ),
        ExtLinesField('PatientPublicationPreferences',
            vocabulary_factory='bika.health.obsolete.CustomPubPrefVocabularyFactory',
            schemata = 'Results Reports',
            widget = MultiSelectionWidget(
                label = _("Default publication preference for Patients"),
                description = _("Select the preferred channels to be used for "
                                "sending the results reports to Patients. "
                                "This setting can be overriden either on "
                                "'Patient publication preferences' tab from "
                                "Client view or on Patient's 'Publication "
                                "preferences' tab.")
                )
        ),
        ExtBooleanField('PatientPublicationAttachmentsPermitted',
            default = False,
            schemata = 'Results Reports',
            widget = BooleanWidget(
                label = _("Results attachments permitted"),
                description = _("File attachments to results, e.g. microscope "
                                "photos, will be included in emails to "
                                "patients if this option is enabled. This "
                                "setting can be overriden either on 'Patient "
                                "publication preferences' tab from Client "
                                "view or on Patient's 'Publication "
                                "preferences' tab.")
                )
        ),
        ExtBooleanField('EnableBikaAnalysisRequestRequestForm',
            schemata="Analyses",
            default=False,
            widget=BooleanWidget(
                label=_("Enable Bika's analysis request form."),
                description=_("It enables the secondary analysis request form. This request has some characteristic "
                              "features as allowing you to register more than one analysis request at the same time. "
                              "It's useful if you are supposed to register a big amount of analysis request at the same "
                              "time.")
            )
        ),
        ExtBooleanField('CaseDoctorIsMandatory',
            schemata="Cases",
            default=True,
            widget=BooleanWidget(
                label=_("Doctor field is mandatory in cases"),
                description=_(
                            "Should the Doctor field be mandatory while "
                            "creating a case?")
                            )
                        ),
        ExtBooleanField('ClientPatientIDUnique',
                        schemata="ID Server",
                        default=False,
                        widget=BooleanWidget(
                            label=_("Client Patient ID must be unique"),
                            description=_("If selected, Client Patient IDs will be forced "
                                          "to be unique")
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
