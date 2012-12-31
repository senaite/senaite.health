""" http://pypi.python.org/pypi/archetypes.schemaextender
"""
from Products.ATContentTypes.interface import IATDocument
from Products.Archetypes.public import *
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.references import HoldingReference
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from bika.health.fields import *
from bika.lims.browser.widgets import DateTimeWidget
from bika.health import bikaMessageFactory as _
from bika.lims import bikaMessageFactory as _b
from bika.health.widgets import *
from bika.lims.interfaces import IBatch
from zope.component import adapts
from zope.interface import implements

class BatchExtender(object):
    adapts(IBatch)
    implements(IOrderableSchemaExtender)

    fields = [
        ExtStringField('ClientID',
            schemata='default',
            required=1,
            widget=StringWidget(
                label=_("Client"),
            )
        ),
        ExtStringField('ClientUID',
            schemata='default',
            widget=StringWidget(
                visible=False,
            ),
        ),
        ExtStringField('DoctorID',
            schemata='default',
            required=0,
            widget=StringWidget(
                label=_("Doctor"),
            )
        ),
        ExtStringField('DoctorUID',
            schemata='default',
            widget=StringWidget(
                visible=False,
            ),
        ),
        ExtStringField('PatientID',
            schemata='default',
            required = 1,
            widget=StringWidget(
                label=_('Patient'),
            ),
        ),
        ExtStringField('PatientUID',
            schemata='default',
            widget=StringWidget(
                visible=False,
            ),
        ),
        ExtDateTimeField('OnsetDate',
            schemata='default',
              widget=DateTimeWidget(
                  label=_('Onset Date'),
              ),
        ),
        ExtStringField('PatientBirthDate',
            schemata='default',
              widget=StringWidget(
                  visible={'view': 'hidden', 'edit': 'hidden'},
              ),
        ),
        ExtRecordsField('PatientAgeAtCaseOnsetDate',
            schemata='default',
            widget=SplittedDateWidget(
                label=_('Patient Age at Case Onset Date'),
            ),
        ),
        ExtBooleanField('OnsetDateEstimated',
            schemata='default',
            default=False,
            widget=BooleanWidget(
                label = _("Onset Date Estimated"),
            ),
        ),
        ExtRecordsField('ProvisionalDiagnosis',
            schemata='default',
            type='provisionaldiagnosis',
            subfields=('Code', 'Title', 'Description', 'Onset', 'Remarks'),
            subfield_sizes={'Code': 7, 'Title': 15, 'Description': 25, 'Onset': 10, 'Remarks': 25},
            widget=CaseProvisionalDiagnosisWidget(
                label='Provisional diagnosis',
            ),
        ),
        ExtTextField('AdditionalNotes',
            schemata='default',
            default_content_type='text/x-web-intelligent',
            allowable_content_types=('text/x-web-intelligent',),
            default_output_type="text/html",
            widget=TextAreaWidget(
                label=_('Additional notes'),
            ),
        ),
        ExtStringField('CaseStatus',
            schemata='default',
            vocabulary='getCaseStatuses',
            widget=MultiSelectionWidget(
                format='checkbox',
                label=_("Case status")
            ),
        ),
        ExtStringField('CaseOutcome',
            schemata='default',
            vocabulary='getCaseOutcomes',
            widget=MultiSelectionWidget(
                format='checkbox',
                label=_("Case outcome")
            ),
        ),
        ExtRecordsField('Symptoms',
            schemata='default',
            type='symptoms',
            subfields=('Code', 'Title', 'Description', 'Onset', 'Remarks'),
            subfield_sizes={'Code': 7, 'Title': 15, 'Description': 25, 'Onset': 10, 'Remarks': 25},
            # widget=CaseSymptomsWidget(
            #     label='Signs and Symptoms',
            # ),
        ),
        ExtRecordsField('AetiologicAgents',
            schemata='default',
            type='aetiologicagents',
            subfields=('Code', 'Title', 'Description', 'Onset', 'Remarks'),
            subfield_sizes={'Title': 15, 'Description': 25, 'Subtype': 10, 'Remarks': 25},
            # widget=CaseAetiologicAgentsWidget(
            #     label='Aetiological Agents',
            # ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        # XXX Schema mods liks this:
        # schema['title'].required = False
        # schema['title'].widget.visible = False
        schematas['default'] = ['id',
                                'title',
                                'description',
                                'BatchID',
                                'PatientID',
                                'ClientID',
                                'ClientBatchID',
                                'DoctorID',
                                'OnsetDate',
                                'PatientAgeAtCaseOnsetDate',
                                'OnsetDateEstimated',
                                'ProvisionalDiagnosis',
                                'Symptoms',
                                'BatchLabels',
                                'CaseStatus',
                                'CaseOutcome',
                                'AetiologicAgents',
                                'AdditionalNotes',
                                'Remarks',
                                'ClientUID',
                                'DoctorUID',
                                'PatientUID',
                                'PatientBirthDate']
        return schematas

    def getFields(self):
        return self.fields

