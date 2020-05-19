# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH.
#
# SENAITE.HEALTH is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.Archetypes import DisplayList
from Products.Archetypes.Widget import BooleanWidget
from Products.Archetypes.Widget import IntegerWidget
from Products.Archetypes.Widget import MultiSelectionWidget
from Products.Archetypes.Widget import StringWidget
from Products.Archetypes.Widget import TextAreaWidget
from Products.Archetypes.interfaces import IVocabulary
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from zope.component import adapts
from zope.interface import implements

from bika.health import bikaMessageFactory as _
from bika.health.utils import get_field_value
from bika.health.widgets import CaseBasalBodyTempWidget
from bika.health.widgets import CaseMenstrualStatusWidget
from bika.health.widgets import CaseSymptomsWidget
from bika.health.widgets import SplittedDateWidget
from bika.health.widgets.casepatientconditionwidget import \
    CasePatientConditionWidget
from bika.lims import api
from bika.lims import bikaMessageFactory as _b
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.fields import ExtBooleanField
from bika.lims.fields import ExtDateTimeField
from bika.lims.fields import ExtIntegerField
from bika.lims.fields import ExtLinesField
from bika.lims.fields import ExtRecordsField
from bika.lims.fields import ExtReferenceField
from bika.lims.fields import ExtStringField
from bika.lims.fields import ExtTextField
from bika.lims.interfaces import IBatch


class getCaseStatus:
    implements(IVocabulary)
    def getDisplayList(self, instance):
        """ return all case statuses"""
        bsc = getToolByName(instance, 'bika_setup_catalog')
        ret = []
        for p in bsc(portal_type = 'CaseStatus',
                      is_active = True,
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
                      is_active = True,
                      sort_on = 'sortable_title'):
            ret.append((p.Title, p.Title))
        return DisplayList(ret)


class BatchSchemaExtender(object):
    adapts(IBatch)
    implements(IOrderableSchemaExtender)

    fields = [
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
                base_query={'is_active': True},
                catalog_name='portal_catalog',
                showOn=True,
                colModel = [{'columnName':'DoctorID','width':'20','label':_('Doctor ID')},
                            {'columnName':'Title','width':'80','label':_('Full Name')},
                            ],
            ),
        ),
        ExtReferenceField('Patient',
            required=1,
            multiValued=0,
            allowed_types = ('Patient',),
            referenceClass = HoldingReference,
            relationship = 'BatchPatient',
            widget=ReferenceWidget(
                label=_("Patient"),
                description="",
                render_own_label=False,
                visible={'edit': 'visible',
                         'view': 'visible'},
                catalog_name='bikahealth_catalog_patient_listing',
                search_fields=('listing_searchable_text',),
                base_query={'is_active': True,
                            'sort_limit': 50,
                            'sort_on': 'getPatientID',
                            'sort_order': 'ascending'},
                colModel=[
                    {'columnName': "getPatientID",
                     'width': '30',
                     'label': _('PID'),
                     'align': 'left'},
                    {'columnName': "getClientPatientID",
                     'width': '30',
                     'label': _('CPID'),
                     'align': 'left'},
                    {'columnName': 'Title',
                     'width': '30',
                     'label': _('Title'),
                     'align': 'left'},
                ],
                showOn=True,
            ),
        ),
        ExtDateTimeField('OnsetDate',
            required = 1,
            widget=DateTimeWidget(
                label=_('Onset Date'),
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
                size=20,
                visible={'edit': 'invisible',
                         'view': 'visible',
                         'add': 'edit'},
                catalog_name='bikahealth_catalog_patient_listing',
                portal_types=('Patient',),
                search_fields=('getClientPatientID',),
                base_query={'is_active': True,
                            'sort_limit': 50,
                            'sort_on': 'getClientPatientID',
                            'sort_order': 'ascending'},
                force_all = False,
                colModel = [
                    {'columnName': "getPatientID",
                     'width': '30',
                     'label': _('PID'),
                     'align': 'left'},
                    {'columnName': "getClientPatientID",
                     'width': '30',
                     'label': _('CPID'),
                     'align': 'left'},
                    {'columnName': 'Title',
                     'width': '30',
                     'label': _('Fullname'),
                     'align': 'left'},
                    # UID is required in colModel
                    {'columnName': 'UID', 'hidden': True},
                ],
                ui_item="getClientPatientID",
                showOn=False,
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
                                'Client',
                                'ClientBatchID',
                                'ClientPatientID',
                                'Patient',
                                'Doctor',
                                'BatchDate',
                                'OnsetDate',
                                'OnsetDateEstimated',
                                'PatientAgeAtCaseOnsetDate',
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
                                'BatchLabels', ]
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
        schema['Remarks'].widget.visible = False
        setup = api.get_setup()
        doctor_required = get_field_value(setup, "CaseDoctorIsMandatory",
                                          default=False)
        schema['Doctor'].required = doctor_required
        schema['Client'].required = True
        return schema
