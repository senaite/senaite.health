from Products.Archetypes.Widget import BooleanWidget
from archetypes.schemaextender.interfaces import ISchemaExtender
from bika.health.fields import *
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
        ExtStringField('PatientConditionsHeightUnits',
            schemata="Cases",
            default="Feet/inches",
            widget=StringWidget(
                label=_("Patient condition height units")
            )
        ),
        ExtStringField('PatientConditionsWeightUnits',
            schemata="Cases",
            default="Lbs",
            widget=StringWidget(
                label=_("Patient condition weight units")
            )
        ),
        ExtStringField('PatientConditionsWaistUnits',
            schemata="Cases",
            default="Inches",
            widget=StringWidget(
                label=_("Patient condition waist units")
            )
        ),
    ]

    def __init__(self, context):
        self.context = context

        for field in self.fields:
            fn = field.getName()
            if not hasattr(context, 'get' + fn):
                context.__setattr__('get' + fn, field_getter(context, fn))
            if not hasattr(context, 'set' + fn):
                context.__setattr__('set' + fn, field_setter(context, fn))

    def getFields(self):
        return self.fields
