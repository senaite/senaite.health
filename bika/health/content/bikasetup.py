from Products.Archetypes.Widget import BooleanWidget
from archetypes.schemaextender.interfaces import ISchemaExtender,\
    IOrderableSchemaExtender
from bika.lims.config import PUBLICATION_PREFS
from bika.lims.fields import *
from bika.health import bikaMessageFactory as _
from bika.lims.interfaces import IBikaSetup
from zope.component import adapts
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
            vocabulary= PUBLICATION_PREFS,
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
