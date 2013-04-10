from Products.Archetypes.Widget import BooleanWidget
from archetypes.schemaextender.interfaces import ISchemaExtender
from bika.lims.fields import *
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IBikaSetup
from zope.component import adapts
from zope.interface import implements


class BikaSetupSchemaExtender(object):
    adapts(IBikaSetup)
    implements(ISchemaExtender)

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
            default="Feet/inches",
            widget=StringWidget(
                label=_("Patient condition height units"),
                description=_("Use '/' symbol to allow multiple-units submission")
            )
        ),
        ExtStringField('PatientConditionsWeightUnits',
            schemata="Cases",
            default="Lbs",
            widget=StringWidget(
                label=_("Patient condition weight units"),
                description=_("Use '/' symbol to allow multiple-units submission")
            )
        ),
        ExtStringField('PatientConditionsWaistUnits',
            schemata="Cases",
            default="Inches",
            widget=StringWidget(
                label=_("Patient condition waist units"),
                description=_("Use '/' symbol to allow multiple-units submission")
            )
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
