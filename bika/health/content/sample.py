# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.Health
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.


""" http://pypi.python.org/pypi/archetypes.schemaextender
"""
from Products.Archetypes.references import HoldingReference
from Products.CMFCore import permissions
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from zope.component import adapts
from zope.interface import implements

from bika.health import bikaMessageFactory as _
from bika.health.catalog import CATALOG_PATIENT_LISTING
from bika.health.permissions import ViewPatients
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.fields import ExtReferenceField
from bika.lims.fields import ExtStringField
from bika.lims.interfaces import ISample


class SampleSchemaExtender(object):
    adapts(ISample)
    implements(ISchemaExtender)

    def __init__(self, context):
        self.context = context

    fields = [
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
                     'align': 'left'},
                    {'columnName': 'getClientPatientID',
                     'width': '20',
                     'label': _('Client PID'),
                     'align': 'left'},
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
                visible={
                    'edit': 'visible',
                    'view': 'visible',
                    'add': 'edit',
                    'header_table': 'visible',
                    'sample_registered': {
                        'view': 'visible',
                        'edit': 'invisible',
                        'add': 'edit'},
                    'to_be_sampled': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'scheduled_sampling': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'sampled': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'to_be_preserved': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'sample_due': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'sample_prep': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'sample_received': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'attachment_due': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'to_be_verified': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'verified': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'published': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'invalid': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'rejected': {
                        'view': 'visible',
                        'edit': 'invisible'},
                },
                catalog_name=CATALOG_PATIENT_LISTING,
                base_query={'inactive_state': 'active'},
                showOn=True,
            ),
        ),

        ExtReferenceField(
            'Patient',
            required=1,
            allowed_types=('Patient',),
            referenceClass=HoldingReference,
            relationship='AnalysisRequestPatient',
            read_permission=ViewPatients,
            write_permission=permissions.ModifyPortalContent,
            widget=ReferenceWidget(
                label=_('Patient'),
                size=20,
                render_own_label=True,
                visible={
                    'edit': 'visible',
                    'view': 'visible',
                    'add': 'edit',
                    'header_table': 'visible',
                    'sample_registered': {
                        'view': 'visible',
                        'edit': 'invisible',
                        'add': 'edit'},
                    'to_be_sampled': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'scheduled_sampling': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'sampled': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'to_be_preserved': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'sample_due': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'sample_prep': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'sample_received': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'attachment_due': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'to_be_verified': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'verified': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'published': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'invalid': {
                        'view': 'visible',
                        'edit': 'invisible'},
                    'rejected': {
                        'view': 'visible',
                        'edit': 'invisible'},
                },
                catalog_name=CATALOG_PATIENT_LISTING,
                base_query={'inactive_state': 'active'},
                colModel=[
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
                    'js_controllers': ['#patient-base-edit', ],
                    'overlay_handler': 'HealthPatientOverlayHandler',
                }
            ),
        ),

    ]

    def getFields(self):
        return self.fields


class SampleSchemaModifier(object):
    adapts(ISample)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        return schema

    def getPatientUID(self):
        """
        Return the patient UID
        """
        field = self.context.getField('Patient', None)
        item = field.get(self.context)
        if item is not None:
            return item.UID()

    def getPatientID(self):
        """
        Return the patient ID
        """
        field = self.context.getField('Patient', None)
        item = field.get(self.context)
        if item is not None:
            return item.getId()
