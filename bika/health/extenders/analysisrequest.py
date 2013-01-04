""" http://pypi.python.org/pypi/archetypes.schemaextender
"""
from Products.ATContentTypes.interface import IATDocument
from Products.Archetypes.public import *
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.references import HoldingReference
from archetypes.schemaextender.interfaces import ISchemaExtender
from bika.health.fields import *
from bika.health import bikaMessageFactory as _
from bika.lims import bikaMessageFactory as _b
from bika.lims.interfaces import IAnalysisRequest
from zope.component import adapts
from zope.interface import implements

class AnalysisRequestExtender(object):
    adapts(IAnalysisRequest)
    implements(ISchemaExtender)

    fields = [
        ExtReferenceField('Doctor',
            required = 0,
            multiValued=0,
            allowed_types = ('Doctor',),
            referenceClass = HoldingReference,
            relationship = 'AnalysisRequestDoctor',
            widget=StringWidget(
                label=_('Doctor'),
            ),
        ),
        ExtComputedField('DoctorUID',
            expression='context.getDoctor() and context.getDoctor().UID() or None',
            widget=ComputedWidget(
                visible=False,
            ),
        ),
        ExtReferenceField('Patient',
            required=0,
            multiValued=0,
            allowed_types = ('Patient',),
            referenceClass = HoldingReference,
            relationship = 'AnalysisRequestPatient',
            widget=StringWidget(
                label=_('Patient'),
            ),
        ),
        ExtComputedField('PatientUID',
            expression='context.getPatient() and context.getPatient().UID() or None',
            widget=ComputedWidget(
                visible=False,
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
