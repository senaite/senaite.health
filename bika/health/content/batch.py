# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

""" http://pypi.python.org/pypi/archetypes.schemaextender
"""
from Products.ATContentTypes.interface import IATDocument
from Products.Archetypes.interfaces import IVocabulary
from Products.Archetypes.public import *
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.widgets import RecordsWidget
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.lims.fields import *
from bika.lims.interfaces import IBatch
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import ReferenceWidget
from bika.health import bikaMessageFactory as _
from bika.lims import bikaMessageFactory as _b
from bika.health.widgets import *
from plone.indexer.decorator import indexer
from zope.component import adapts
from zope.interface import implements
from bika.health.widgets.casepatientconditionwidget import CasePatientConditionWidget
from bika.lims.interfaces import IBatchSearchableText
try:
    from zope.component.hooks import getSite
except:
    # Plone < 4.3
    from zope.app.component.hooks import getSite

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
            ret.append((p.Title, p.Title))
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
            ret.append((p.Title, p.Title))
        return DisplayList(ret)

@indexer(IBatch)
def getPatientID(instance):
    item = instance.Schema()['Patient'].get(instance)
    value = item and item.getPatientID() or ''
    return value

@indexer(IBatch)
def getPatientUID(instance):
    item = instance.Schema()['Patient'].get(instance)
    value = item and item.UID() or ''
    return value

@indexer(IBatch)
def getPatientTitle(instance):
    return PatientTitleGetter(instance)


def PatientTitleGetter(obj):
    item = obj.Schema()['Patient'].get(obj)
    value = item and item.Title() or ''
    return value

@indexer(IBatch)
def getDoctorID(instance):
    item = instance.Schema()['Doctor'].get(instance)
    value = item and item.Schema()['DoctorID'].get(item) or ''
    return value

@indexer(IBatch)
def getDoctorUID(instance):
    item = instance.Schema()['Doctor'].get(instance)
    value = item and item.UID() or ''
    return value

@indexer(IBatch)
def getDoctorTitle(instance):
    item = instance.Schema()['Doctor'].get(instance)
    value = item and item.Title() or ''
    return value

@indexer(IBatch)
def getClientID(instance):
    item = instance.Schema()['Client'].get(instance)
    value = item and item.Schema()['ClientID'].get(item) or ''
    return value

@indexer(IBatch)
def getClientUID(instance):
    item = instance.Schema()['Client'].get(instance)
    value = item and item.UID() or ''
    return value

@indexer(IBatch)
def getClientTitle(instance):
    item = instance.Schema()['Client'].get(instance)
    value = item and item.Title() or ''
    return value

@indexer(IBatch)
def getClientPatientID(instance):
    return ClientPatientIDGetter(instance)


def ClientPatientIDGetter(obj):
    item = obj.Schema()['Patient'].get(obj)
    value = item and item.getClientPatientID() or ''
    return value


class BatchSchemaExtender(object):
    adapts(IBatch)
    implements(IOrderableSchemaExtender)

    fields = [
        # ExtComputedField('ClientID',
        #     expression="context.Schema()['Client'].get(context) and context.Schema()['Client'].get(context).ID() or None",
        # ),
        # ExtComputedField('ClientUID',
        #     expression="context.Schema()['Client'].get(context) and context.Schema()['Client'].get(context).UID() or None",
        # ),
        # ExtComputedField('ClientTitle',
        #     expression="context.Schema()['Client'].get(context) and context.Schema()['Client'].get(context).Title() or None",
        # ),
        ExtReferenceField('Doctor',
            required=1,
            multiValued=0,
            allowed_types = ('Doctor',),
            referenceClass = HoldingReference,
            relationship = 'BatchDoctor',
            widget=ReferenceWidget(
                label=_("Doctor"),
                description="",
                render_own_label=False,
                visible={'edit': 'visible', 'view': 'visible'},
                base_query={'inactive_state': 'active'},
                catalog_name='portal_catalog',
                showOn=True,
                colModel = [{'columnName':'DoctorID','width':'20','label':_('Doctor ID')},
                            {'columnName':'Title','width':'80','label':_('Full Name')},
                            ],
                add_button={
                    'visible': True,
                    'url': 'doctors/portal_factory/Doctor/new/edit',
                    'return_fields': ['Firstname', 'Surname'],
                    'js_controllers': ['#doctor-base-edit',],
                    'overlay_handler': 'HealthDoctorOverlayHandler',
                },
                edit_button={
                    'visible': True,
                    # url with the root to create/edit a object.
                    'url': 'doctors/portal_factory/Doctor',
                    'return_fields': ['Firstname', 'Surname'],
                    'js_controllers': ['#doctor-base-edit',],
                    'overlay_handler': 'HealthDoctorOverlayHandler',
                }
            ),
        ),
        # ExtComputedField('DoctorID',
        #     expression="context.Schema()['Doctor'].get(context) and context.Schema()['Doctor'].get(context).ID() or None",
        # ),
        # ExtComputedField('DoctorUID',
        #     expression="context.Schema()['Doctor'].get(context) and context.Schema()['Doctor'].get(context).UID() or None",
        # ),
        # ExtComputedField('DoctorTitle',
        #     expression="context.Schema()['Doctor'].get(context) and context.Schema()['Doctor'].get(context).Title() or None",
        # ),
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
                catalog_name='bikahealth_catalog_patient_listing',
                search_fields=('SearchableText',),
                showOn=False,
                delay=1000,
                minLength=2,
                colModel = [{'columnName':'getPatientID','width':'20','label':_('Patient ID')},
                            {'columnName':'Title','width':'40','label':_('Full Name')},
                            {'columnName':'getPatientIdentifiersStr', 'width':'40','label':_('Additional Identifiers')}],
                add_button={
                    'visible': True,
                    'url': 'patients/portal_factory/Patient/new/edit',
                    'return_fields': ['Firstname', 'Surname'],
                    'js_controllers': ['#patient-base-edit',],
                    'overlay_handler': 'HealthPatientOverlayHandler',
                },
                edit_button={
                    'visible': True,
                    # url with the root to create/edit a object.
                    'url': 'patients/portal_factory/Patient',
                    'return_fields': ['Firstname', 'Surname'],
                    'js_controllers': ['#patient-base-edit',],
                    'overlay_handler': 'HealthPatientOverlayHandler',
                }
            ),
        ),
        # ExtComputedField('PatientID',
        #     expression="context.Schema()['Patient'].get(context) and context.Schema()['Patient'].get(context).ID() or None",
        # ),
        # ExtComputedField('PatientUID',
        #     expression="context.Schema()['Patient'].get(context) and context.Schema()['Patient'].get(context).UID() or None",
        # ),
        # ExtComputedField('PatientTitle',
        #     expression="context.Schema()['Patient'].get(context) and context.Schema()['Patient'].get(context).Title() or None",
        # ),
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
            # Temporary fix: https://github.com/bikalabs/bika.health/issues/89
            #required_subfields=('Title'),
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
                         'url': 'getsymptomsbytitle',
                         'showOn': True,
                         'width': "650px",
                     },
                     'Code': {
                         'colModel': [{'columnName':'Code', 'width':'10', 'label':_('Code')},
                                      {'columnName':'Title', 'width':'30', 'label':_('Title')},
                                      {'columnName':'Description', 'width':'60', 'label':_('Description')}],
                         'url': 'getsymptomsbycode',
                         'showOn': True,
                         'width': "650px",
                     },
                     'Description': {
                         'colModel': [{'columnName':'Code', 'width':'10', 'label':_('Code')},
                                      {'columnName':'Title', 'width':'30', 'label':_('Title')},
                                      {'columnName':'Description', 'width':'60', 'label':_('Description')}],
                         'url': 'getsymptomsbydesc',
                         'showOn': True,
                         'width': "650px",
                     },
                 },
             ),
        ),
        ExtTextField('AdditionalNotes',
            default_content_type='text/plain',
            allowable_content_types = ('text/plain', ),
            default_output_type="text/plain",
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
            # Temporary fix: https://github.com/bikalabs/bika.health/issues/89
            # required_subfields=('Title'),
            widget=RecordsWidget(
                label='Aetiologic agents',
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
        ExtStringField(
            'ClientPatientID',
            required=0,
            widget=ReferenceWidget(
                label=_b("Client Patient ID"),
                size=12,
                colModel=[
                    {'columnName': 'id',
                                    'width': '20',
                                    'label': _('Patient ID'),
                                    'align':'left'},
                    {'columnName': 'getClientPatientID',
                                    'width': '20',
                                    'label': _('Client PID'),
                                    'align':'left'},
                    {'columnName': 'Title',
                                    'width': '60',
                                    'label': _('Fullname'),
                                    'align': 'left'},
                    {'columnName': 'UID', 'hidden': True},
                ],
                ui_item='ClientPatientID',
                search_query='',
                discard_empty=('ClientPatientID',),
                search_fields=('getClientPatientID',),
                portal_types=('Patient',),
                render_own_label=False,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'visible'},
                catalog_name='bikahealth_catalog_patient_listing',
                base_query={'inactive_state': 'active'},
                showOn=True,
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
                                'ClientPatientID',
                                'Patient',
                                # 'PatientID',
                                # 'PatientUID',
                                # 'PatientTitle',
                                'Client',
                                # 'ClientID',
                                # 'ClientUID',
                                # 'ClientTitle',
                                'ClientBatchID',
                                'Doctor',
                                # 'DoctorID',
                                # 'DoctorUID',
                                # 'DoctorTitle',
                                'BatchDate',
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
                                'PatientBirthDate',
                                'BatchLabels',
                                'InheritedObjects',
                                'InheritedObjectsUI',]
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
        schema['BatchDate'].widget.visible = False
        schema['InheritedObjectsUI'].widget.visible = False
        schema['Doctor'].required = self.isCaseDoctorIsMandatory()
        return schema

    def isCaseDoctorIsMandatory(self):
        """
        Returns whether the Doctor field is mandatory or not in cases object.
        :return: boolean
        """
        if hasattr(self.context, 'bika_setup'):
            return self.context.bika_setup.CaseDoctorIsMandatory

        # If this object is being created right now, then it doesn't have bika_setup, get bika_setup from site root.
        plone = getSite()
        if not plone:
            plone = get_site_from_context(self.context)
        return plone.bika_setup.CaseDoctorIsMandatory


def get_site_from_context(context):
    """
    Sometimes getSite() method can return None, in that case we can find site root in parents of an object.
    :param context: context to go through parents of, until we reach the site root
    :return: site root
    """
    if not ISiteRoot.providedBy(context):
        return context
    else:
        for item in context.aq_chain:
            if ISiteRoot.providedBy(item):
                return item


class BatchSearchableText(object):
    """
    This class is used as an adapter in order to obtain field or methods
    results as string values for SearchableText index in batches (cases).
    """
    implements(IBatchSearchableText)

    def __init__(self, context):
        # Each adapter takes the object itself as the construction
        # parameter and possibly provides other parameters for the
        # interface adaption
        self.context = context

    def get_plain_text_fields(self):
        """
        This function returns field or methods results to be used in
        searchable text.
        :return: A list of strings as searchable text options.
        """
        client_patient_id = ClientPatientIDGetter(self.context)
        client_patient_name = PatientTitleGetter(self.context)
        return [client_patient_id, client_patient_name]
