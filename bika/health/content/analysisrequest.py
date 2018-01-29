# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

""" http://pypi.python.org/pypi/archetypes.schemaextender
"""
from Products.Archetypes.references import HoldingReference
from Products.CMFCore import permissions
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from plone.indexer.decorator import indexer
from zope.component import adapts
from zope.interface import implements

from bika.health import bikaMessageFactory as _
from bika.health.permissions import ViewPatients
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.fields import BooleanField
from bika.lims.fields import BooleanWidget
from bika.lims.fields import ExtReferenceField
from bika.lims.fields import ExtStringField
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IBikaCatalog
from bika.lims.interfaces import IBikaCatalogAnalysisRequestListing


# Defining the indexes for this extension. Since this is an extension, no
# getter is created so we need to create indexes in that way.
# TODO-catalog: delete this index
@indexer(IAnalysisRequest, IBikaCatalog)
def getPatientUID(instance):
    field = instance.getField('Patient', '')
    item = field.get(instance) if field else None
    value = item and item.UID() or ''
    return value


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getPatientUID(instance):
    field = instance.getField('Patient', '')
    item = field.get(instance) if field else None
    value = item and item.UID() or ''
    return value


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getDoctorUID(instance):
    field = instance.getField('Doctor', '')
    item = field.get(instance) if field else None
    value = item and item.UID() or ''
    return value


# We use this index to sort columns and filter lists
@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getPatient(instance):
    field = instance.getField('Patient', '')
    item = field.get(instance) if field else None
    value = item and item.Title() or ''
    return value


# We use this index to sort columns and filter lists
@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getPatientID(instance):
    field = instance.getField('Patient', '')
    item = field.get(instance) if field else None
    value = item and item.getId() or ''
    return value


class AnalysisRequestSchemaExtender(object):
    adapts(IAnalysisRequest)
    implements(IOrderableSchemaExtender)

    def __init__(self, context):
        self.context = context

    fields = [
        ExtReferenceField(
            'Doctor',
            allowed_types=('Doctor',),
            referenceClass = HoldingReference,
            relationship = 'AnalysisRequestDoctor',
            widget=ReferenceWidget(
                label=_('Doctor'),
                size=20,
                render_own_label=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'edit',
                         'header_table': 'visible',
                         'secondary': 'disabled'},
                catalog_name='portal_catalog',
                base_query={'inactive_state': 'active'},
                showOn=True,
                add_button={
                    'visible': True,
                    'url': 'doctors/portal_factory/Doctor/new/edit',
                    'return_fields': ['Firstname', 'Surname'],
                }
            ),
        ),

        ExtReferenceField(
            'Patient',
            required=1,
            allowed_types = ('Patient',),
            referenceClass = HoldingReference,
            relationship = 'AnalysisRequestPatient',
            read_permission=ViewPatients,
            write_permission=permissions.ModifyPortalContent,
            widget=ReferenceWidget(
                label=_('Patient'),
                size=20,
                render_own_label=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'edit',
                         'secondary': 'disabled'},
                catalog_name='bikahealth_catalog_patient_listing',
                base_query={'inactive_state': 'active'},
                colModel = [
                    {'columnName': 'Title', 'width': '30', 'label': _(
                        'Title'), 'align': 'left'},
                    # UID is required in colModel
                    {'columnName': 'UID', 'hidden': True},
                ],
                showOn=True,
                add_button={
                    'visible': True,
                    'url': 'patients/portal_factory/Patient/new/edit',
                    'return_fields': ['Firstname', 'Surname'],
                    'js_controllers': ['#patient-base-edit',],
                    'overlay_handler': 'HealthPatientOverlayHandler',
                }
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

        ExtStringField(
            'ClientPatientID',
            searchable=True,
            required=1,
            read_permission=ViewPatients,
            write_permission=permissions.ModifyPortalContent,
            widget=ReferenceWidget(
                label=_("Client Patient ID"),
                size=20,
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
                ui_item='getClientPatientID',
                search_query='',
                discard_empty=('ClientPatientID',),
                search_fields=('ClientPatientID',),
                portal_types=('Patient',),
                render_own_label=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'add': 'edit',
                         },
                catalog_name='bikahealth_catalog_patient_listing',
                base_query={'inactive_state': 'active'},
                showOn=True,
            ),
        ),
    ]

    def getOrder(self, schematas):
        default = schematas['default']
        default.remove('Patient')
        default.remove('Doctor')
        default.remove('ClientPatientID')
        default.insert(default.index('Template'), 'ClientPatientID')
        default.insert(default.index('Template'), 'Patient')
        default.insert(default.index('Template'), 'Doctor')
        schematas['default'] = default
        return schematas

    def getFields(self):
        return self.fields


class AnalysisRequestSchemaModifier(object):
    adapts(IAnalysisRequest)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        schema['Batch'].widget.label = _("Case")
        return schema
