""" http://pypi.python.org/pypi/archetypes.schemaextender
"""
from Products.ATContentTypes.interface import IATDocument
from Products.Archetypes.interfaces import IVocabulary
from Products.Archetypes.public import *
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.widgets import RecordsWidget
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.lims.fields import *
from bika.lims.interfaces import IBatch
from bika.health.interfaces import IBikaPatientCatalog
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import ReferenceWidget
from bika.health import bikaMessageFactory as _
from bika.lims import bikaMessageFactory as _b
from bika.health.widgets import *
from plone.indexer.decorator import indexer
from zope.component import adapts
from zope.interface import implements
from bika.health.widgets.casepatientconditionwidget import CasePatientConditionWidget

class getCaseSyndromicClassification:
    implements(IVocabulary)
    def getDisplayList(self, instance):
        """ return all case syndromic classifications """
        bsc = getToolByName(instance, 'bika_setup_catalog')
        ret = []
        for p in bsc(portal_type = 'CaseSyndromicClassification',
                      inactive_state = 'active',
                      sort_on = 'sortable_title'):
            ret.append((p.UID, p.Title))
        return DisplayList(ret)

class getCaseStatus:
    implements(IVocabulary)
    def getDisplayList(self, instance):
        """ return all case statuses"""
        bsc = getToolByName(instance, 'bika_setup_catalog')
        ret = []
        for p in bsc(portal_type = 'CaseStatus',
                      inactive_state = 'active',
                      sort_on = 'sortable_title'):
            ret.append((p.UID, p.Title))
        return DisplayList(ret)

class getCaseOutcome:
    implements(IVocabulary)
    def getDisplayList(self, instance):
        """ return all case Outcomes"""
        bsc = getToolByName(instance, 'bika_setup_catalog')
        ret = []
        for p in bsc(portal_type = 'CaseOutcome',
                      inactive_state = 'active',
                      sort_on = 'sortable_title'):
            ret.append((p.UID, p.Title))
        return DisplayList(ret)

@indexer(IBatch)
def getPatientID(instance):
    patient = instance.Schema()['Patient'].get(instance)
    return patient and patient.getPatientID() or ''

@indexer(IBatch)
def getPatientTitle(instance):
    patient = instance.Schema()['Patient'].get(instance)
    return patient and patient.getPatientTitle() or ''

@indexer(IBatch)
def getDoctorID(instance):
    doctor = instance.Schema()['Doctor'].get(instance)
    return doctor and doctor.getDoctorID() or ''

@indexer(IBatch)
def getDoctorTitle(instance):
    doctor = instance.Schema()['Doctor'].get(instance)
    return doctor and doctor.getDoctorTitle() or ''

@indexer(IBatch)
def getClientID(instance):
    client = instance.Schema()['Client'].get(instance)
    return client and client.getClientID() or ''

@indexer(IBatch)
def getClientTitle(instance):
    client = instance.Schema()['Client'].get(instance)
    return client and client.getClientTitle() or ''


class BatchSchemaExtender(object):
    adapts(IBatch)
    implements(IOrderableSchemaExtender)

    fields = [
        ExtReferenceField('Client',
            required = 1,
            multiValued=0,
            allowed_types = ('Client',),
            referenceClass = HoldingReference,
            relationship = 'BatchClient',
            widget=StringWidget(
                label=_('Client'),
                visible=False,
            ),
        ),
        ExtStringField('ClientID',
            required = 1,
            widget=StringWidget(
                label=_('Client'),
            ),
        ),
        ExtComputedField('ClientUID',
            expression="context.getClient() and context.getClient().UID() or None",
        ),
        ExtComputedField('ClientTitle',
            expression="context.getClient() and context.getClient().Title() or None",
        ),
        ExtReferenceField('Doctor',
            required = 1,
            multiValued=0,
            allowed_types = ('Doctor',),
            referenceClass = HoldingReference,
            relationship = 'BatchDoctor',
            widget=StringWidget(
                label=_('Doctor'),
                visible=False,
            ),
        ),
        ExtStringField('DoctorID',
            required = 1,
            widget=StringWidget(
                label=_('Doctor'),
            ),
        ),
        ExtComputedField('DoctorUID',
            expression="context.getDoctor() and context.getDoctor().UID() or None",
        ),
        ExtComputedField('DoctorTitle',
            expression="context.getDoctor() and context.getDoctor().Title() or None",
        ),
        ExtReferenceField('Patient',
            required = 1,
            multiValued=0,
            allowed_types = ('Patient',),
            referenceClass = HoldingReference,
            relationship = 'BatchPatient',
            widget=ReferenceWidget(
                label=_("Patient"),
                description="",
                render_own_label=False,
                visible={'edit': 'visible', 'view': 'visible'},
                base_query={'inactive_state': 'active'},
                catalog_name='bika_patient_catalog',
                showOn=True,
            ),
        ),
        ExtComputedField('PatientID',
            expression="context.Schema()['Patient'].get(context) and context.Schema()['Patient'].get(context).ID() or None",
        ),
        ExtComputedField('PatientUID',
            expression="context.Schema()['Patient'].get(context) and context.Schema()['Patient'].get(context).UID() or None",
        ),
        ExtComputedField('PatientTitle',
            expression="context.Schema()['Patient'].get(context) and context.Schema()['Patient'].get(context).Title() or None",
        ),
        ExtDateTimeField('OnsetDate',
              widget=DateTimeWidget(
                  label=_('Onset Date'),
              ),
        ),
        ExtStringField('PatientBirthDate',
              widget=StringWidget(
                  visible=False,
              ),
        ),
        ExtRecordsField('PatientAgeAtCaseOnsetDate',
            widget=SplittedDateWidget(
                label=_('Patient Age at Case Onset Date'),
            ),
        ),
        ExtBooleanField('OnsetDateEstimated',
            default=False,
            widget=BooleanWidget(
                label = _("Onset Date Estimated"),
            ),
        ),
        ExtRecordsField('ProvisionalDiagnosis',
            type='provisionaldiagnosis',
            subfields=('Code', 'Title', 'Description', 'Onset'),
            required_subfields=('Title'),
            subfield_sizes={'Code': 7,
                            'Title': 20,
                            'Description': 35,
                            'Onset': 10},
            subfield_labels={'Code': _('Code'),
                             'Title': _('Provisional diagnosis'),
                             'Description': _('Description'),
                             'Onset': _('Onset')},
             subfield_types={'Onset': 'datepicker_nofuture'},
             widget=RecordsWidget(
                 label='Provisional diagnosis',
                 combogrid_options={
                     'Title': {
                         'colModel': [{'columnName':'Code', 'width':'10', 'label':_('Code')},
                                      {'columnName':'Title', 'width':'30', 'label':_('Title')},
                                      {'columnName':'Description', 'width':'60', 'label':_('Description')}],
                         'url': 'getsymptoms',
                         'showOn': True,
                         'width': "650px",
                     },
                 },
             ),
        ),
        ExtTextField('AdditionalNotes',
            default_content_type='text/x-web-intelligent',
            allowable_content_types=('text/x-web-intelligent',),
            default_output_type="text/html",
            widget=TextAreaWidget(
                label=_('Additional notes'),
            ),
        ),
        ExtLinesField('CaseStatus',
            vocabulary=getCaseStatus(),
            widget=MultiSelectionWidget(
                format='checkbox',
                label=_("Case status")
            ),
        ),
        ExtLinesField('CaseOutcome',
            vocabulary=getCaseOutcome(),
            widget=MultiSelectionWidget(
                format='checkbox',
                label=_("Case outcome")
            ),
        ),
        ExtRecordsField('Symptoms',
            type='symptoms',
            subfields=('UID', 'Title', 'Description', 'Severity'),
            widget=CaseSymptomsWidget(
                label='Symptoms',
            ),
        ),
        ExtRecordsField('AetiologicAgents',
            type='aetiologicagents',
            subfields=('Title', 'Description', 'Subtype'),
            subfield_sizes={'Title': 15,
                            'Description': 25,
                            'Subtype': 10},
            subfield_labels={'Title': _('Aetiologic agent'),
                             'Description': _b('Description'),
                             'Subtype': _('Subtype')},
            required_subfields=('Title'),
            widget=RecordsWidget(
                label='Signs and Symptoms',
                combogrid_options={
                    'Title': {
                        'colModel': [{'columnName':'Title', 'width':'30', 'label':_('Aetiologic agent')},
                                     {'columnName':'Description', 'width':'60', 'label':_b('Description')},
                                     {'columnName':'Subtype', 'width':'30', 'label':_('Subtype')}],
                        'url': 'getaetiologicagents',
                        'showOn': True,
                        'width': "650px",
                    },
                },
            ),
        ),
        ExtIntegerField('HoursFasting',
            required = 0,
            widget=IntegerWidget(
                label=_('Hours fasting'),
            ),
        ),
        ExtRecordsField('PatientCondition',
            widget=CasePatientConditionWidget(
                label='Patient condition',
            ),
        ),
        ExtRecordsField('MenstrualStatus',
            widget=CaseMenstrualStatusWidget(
                label='Menstrual status',
            ),
        ),
        ExtRecordsField('BasalBodyTemperature',
            widget=CaseBasalBodyTempWidget(
                label='Basal body temperature',
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        schematas['default'] = ['id',
                                'title',
                                'description',
                                'BatchID',
                                'Patient',
                                'PatientID',
                                'PatientUID',
                                'PatientTitle',
                                'Client',
                                'ClientID',
                                'ClientUID',
                                'ClientTitle',
                                'ClientBatchID',
                                'Doctor',
                                'DoctorID',
                                'DoctorUID',
                                'DoctorTitle',
                                'OnsetDate',
                                'PatientAgeAtCaseOnsetDate',
                                'OnsetDateEstimated',
                                'HoursFasting',
                                'PatientCondition',
                                'BasalBodyTemperature',
                                'MenstrualStatus',
                                'Symptoms',
                                'ProvisionalDiagnosis',
                                'CaseStatus',
                                'CaseOutcome',
                                'AetiologicAgents',
                                'AdditionalNotes',
                                'Remarks',
                                'ClientUID',
                                'DoctorUID',
                                'PatientUID',
                                'PatientBirthDate',
                                'BatchLabels']
        return schematas

    def getFields(self):
        return self.fields

class BatchSchemaModifier(object):
    adapts(IBatch)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        schema['title'].required = False
        schema['title'].widget.visible = False
        schema['description'].required = False
        schema['description'].widget.visible = False
        schema['BatchLabels'].widget.visible = False
        schema['ClientBatchID'].widget.label = _("Client Case ID")
        return schema
