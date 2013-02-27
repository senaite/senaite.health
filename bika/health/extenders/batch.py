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
from bika.health.fields import *
from bika.lims.browser.widgets import DateTimeWidget
from bika.health import bikaMessageFactory as _
from bika.lims import bikaMessageFactory as _b
from bika.health.widgets import *
from bika.lims.interfaces import IBatch
from zope.component import adapts
from zope.interface import implements

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
        ExtReferenceField('Patient',
            required = 1,
            multiValued=0,
            allowed_types = ('Patient',),
            referenceClass = HoldingReference,
            relationship = 'BatchPatient',
            widget=StringWidget(
                label=_('Patient'),
                visible=False,
            ),
        ),
        ExtStringField('PatientID',
            required = 1,
            widget=StringWidget(
                label=_('Patient'),
            ),
        ),
        ExtComputedField('PatientUID',
            expression="context.getPatient() and context.getPatient().UID() or None",
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
        ExtLinesField('CaseSyndromicClassification',
            vocabulary = getCaseSyndromicClassification(),
            widget=MultiSelectionWidget(
                label=_("Batch labels"),
                format="checkbox",
            )
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
            subfields=('Code', 'Title', 'Description', 'Onset'),
            subfield_sizes={'Code': 7,
                            'Title': 15,
                            'Description': 25,
                            'Onset': 10},
            subfield_labels={'Code': _('Code'),
                             'Title': _('Symptom'),
                             'Description': _('Description'),
                             'Onset': _('Onset')},
            required_subfields=('Title'),
            subfield_types={'Onset': 'datepicker_nofuture'},
            widget=RecordsWidget(
                label='Signs and Symptoms',
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
    ]

    def __init__(self, context):
        self.context = context

        for field in self.fields:
            fn = field.getName()
            if not hasattr(context, 'get'+fn):
                context.__setattr__('get'+fn, field_getter(context, fn))
            if not hasattr(context, 'set'+fn):
                context.__setattr__('set'+fn, field_setter(context, fn))

    def getOrder(self, schematas):
        schematas['default'] = ['id',
                                'title',
                                'description',
                                'BatchID',
                                'Patient',
                                'PatientID',
                                'PatientUID',
                                'Client',
                                'ClientID',
                                'ClientUID',
                                'ClientBatchID',
                                'Doctor',
                                'DoctorID',
                                'DoctorUID',
                                'OnsetDate',
                                'PatientAgeAtCaseOnsetDate',
                                'OnsetDateEstimated',
                                'ProvisionalDiagnosis',
                                'Symptoms',
                                'CaseSyndromicClassification',
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

    def getClientID(self):
        return self.getClient() and self.getClient().ID() or None

    def setClientID(self, value=None):
        self.setClient(None)
        if value:
            client = self.portal_catalog(portal_type='Client', ID=value)
            if client:
                client = client[0].getObject()
                self.setClient(client.UID())

    def getPatientID(self):
        return self.getPatient() and self.getPatient().ID() or None

    def setPatientID(self, value=None):
        self.setPatient(None)
        if value:
            bpc = getToolByName(self.context, 'bika_patient_catalog')
            patient = bpc(portal_type='Patient', ID=value)
            if patient:
                patient = patient[0].getObject()
                self.setPatient(patient.UID())

    def getDoctorID(self):
        return self.getClient() and self.getClient().ID() or None

    def setDoctorID(self, value=None):
        self.setDoctor(None)
        if value:
            doctor = self.portal_catalog(portal_type='Doctor', ID=value)
            if doctor:
                doctor = doctor[0].getObject()
                self.setDoctor(doctor.UID())


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
        return schema


