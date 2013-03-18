from Products.Archetypes.Widget import BooleanWidget
from archetypes.schemaextender.interfaces import ISchemaExtender
from bika.health.fields import ExtBooleanField
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
            )
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
