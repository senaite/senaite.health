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

""" http://pypi.python.org/pypi/archetypes.schemaextender
"""
from Products.Archetypes.references import HoldingReference
from Products.CMFCore import permissions
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from zope.component import adapts
from zope.interface import implements

from bika.health import bikaMessageFactory as _
from bika.health.permissions import ViewPatients
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.fields import ExtBooleanField
from bika.lims.fields import BooleanWidget
from bika.lims.fields import ExtReferenceField
from bika.lims.fields import ExtStringField
from bika.lims.interfaces import IAnalysisRequest


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
                visible={'add': 'edit',
                         'secondary': 'disabled'},
                catalog_name='portal_catalog',
                base_query={'is_active': True,},
                minLength=3,
                showOn=True,
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
                visible={'add': 'edit',
                         'secondary': 'disabled'},
                catalog_name='bikahealth_catalog_patient_listing',
                search_fields=('listing_searchable_text',),
                base_query={'is_active': True,
                            'sort_limit': 50,
                            'sort_on': 'getPatientID',
                            'sort_order': 'ascending'},
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
                ],
                minLength=3,
                showOn=True,
            ),
        ),

        ExtStringField(
            'ClientPatientID',
            searchable=True,
            required=0,
            read_permission=ViewPatients,
            write_permission=permissions.ModifyPortalContent,
            widget=ReferenceWidget(
                label=_("Client Patient ID"),
                size=20,
                render_own_label=True,
                visible={'add': 'edit',
                         'secondary': 'disabled'},
                catalog_name='bikahealth_catalog_patient_listing',
                portal_types=('Patient',),
                search_fields=('getClientPatientID',),
                base_query={'is_active': True,
                            'sort_limit': 50,
                            'sort_on': 'getClientPatientID',
                            'sort_order': 'ascending'},
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
                ],
                ui_item="getClientPatientID",
                minLength=3,
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
