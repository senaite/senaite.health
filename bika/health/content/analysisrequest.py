""" http://pypi.python.org/pypi/archetypes.schemaextender
"""
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from bika.health import bikaMessageFactory as _
from bika.health.fields import *
from bika.lims import bikaMessageFactory as _b
from bika.lims.adapters.widgetvisibility import WidgetVisibility as _WV
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.vocabularies import CatalogVocabulary
from Products.Archetypes.public import ComputedWidget
from Products.Archetypes.references import HoldingReference
from Products.ATContentTypes.interface import IATDocument
from zope.component import adapts
from zope.interface import implements


class AnalysisRequestExtender(object):
    adapts(IAnalysisRequest)
    implements(IOrderableSchemaExtender)

    fields = [
        ExtReferenceField(
            'Doctor',
            allowed_types=('Doctor',),
            referenceClass = HoldingReference,
            relationship = 'AnalysisRequestDoctor',
            widget=ReferenceWidget(
                label=_('Doctor'),
                size=12,
                render_own_label=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'visible'},
                catalog_name='portal_catalog',
                base_query={'inactive_state': 'active'},
                showOn=True,
            ),
        ),

        ExtComputedField(
            'DoctorUID',
            expression='context.getDoctor() and context.getDoctor().UID() or None',
            widget=ComputedWidget(
                visible=False,
            ),
        ),

        ExtReferenceField(
            'Patient',
            required=1,
            allowed_types = ('Patient',),
            referenceClass = HoldingReference,
            relationship = 'AnalysisRequestPatient',
            widget=ReferenceWidget(
                label=_('Patient'),
                size=12,
                render_own_label=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'visible'},
                catalog_name='bika_patient_catalog',
                base_query={'inactive_state': 'active'},
                showOn=True,
            ),
        ),

        ExtComputedField(
            'PatientUID',
            expression='context.getPatient() and context.getPatient().UID() or None',
            widget=ComputedWidget(
                visible=False,
            ),
        ),

        BooleanField(
            'PanicEmailAlertToClientSent',
            default=False,
            widget=BooleanWidget(
                visible={'edit': 'invisible', 
                         'view': 'invisible', 
                         'add': 'invisible'},
            ),
        ),
    ]

    def getOrder(self, schematas):
        default = schematas['default']
        default.remove('Patient')
        default.remove('Doctor')
        default.insert(default.index('Template'), 'Patient')
        default.insert(default.index('Patient'), 'Doctor')
        schematas['default'] = default
        return schematas

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
