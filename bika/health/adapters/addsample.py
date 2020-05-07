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

from zope.component import adapts

from bika.health.interfaces import IDoctor
from bika.health.interfaces import IPatient
from bika.health.utils import is_internal_client
from bika.health.utils import resolve_query_for_shareable
from bika.lims import api
from bika.lims.adapters.addsample import AddSampleObjectInfoAdapter
from bika.lims.interfaces import IAddSampleFieldsFlush
from bika.lims.interfaces import IBatch
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IGetDefaultFieldValueARAddHook


class AddFormFieldDefaultValueAdapter(object):
    """Generic adapter for objects retrieval based on request uid and field name
    """

    def __init__(self, request):
        self.request = request

    def get_object_from_request_field(self, field_name):
        """Returns the object for the field_name specified in the request
        """
        uid = self.request.get(field_name)
        return api.get_object_by_uid(uid, default=None)


class ClientDefaultFieldValue(AddFormFieldDefaultValueAdapter):
    """Adapter that returns the default value for field Client in Sample form
    """

    adapts(IGetDefaultFieldValueARAddHook)

    def __call__(self, context):

        if IClient.providedBy(context):
            return context

        # Try to get the client from selected Batch
        batch = BatchDefaultFieldValue(self.request)(context)
        client = batch and batch.getClient() or None
        if client:
            return client

        # Try to get the client from selected Patient
        patient = PatientDefaultFieldValue(self.request)(context)
        client = patient and patient.getClient() or None
        if client:
            return client

        # Try to get the client from selected Doctor
        doctor = DoctorDefaultFieldValue(self.request)(context)
        client = doctor and doctor.getPrimaryReferrer() or None
        if client:
            return client

        # Try with client object explicitly defined in request
        return self.get_object_from_request_field("Client")


class PatientDefaultFieldValue(AddFormFieldDefaultValueAdapter):
    """Adapter that returns the default value for field Patient in Sample form
    """
    adapts(IGetDefaultFieldValueARAddHook)

    def __call__(self, context):
        if IPatient.providedBy(context):
            return context

        # Try to get the client from selected Batch
        batch = BatchDefaultFieldValue(self.request)(context)
        patient = batch and batch.getField("Patient").get(context) or None
        if patient:
            return patient

        # Try with patient explicitly defined in request
        return self.get_object_from_request_field("Patient")


class DoctorDefaultFieldValue(AddFormFieldDefaultValueAdapter):
    """Adapter that returns the default value for field Doctor in Sample form
    """
    adapts(IGetDefaultFieldValueARAddHook)

    def __call__(self, context):
        if IDoctor.providedBy(context):
            return context

        # Try to get the client from selected Batch
        batch = BatchDefaultFieldValue(self.request)(context)
        doctor = batch and batch.getField("Doctor").get(context) or None
        if doctor:
            return doctor

        # Try with doctor explicitly defined in request
        return self.get_object_from_request_field("Doctor")


class BatchDefaultFieldValue(AddFormFieldDefaultValueAdapter):
    """Adapter that returns the default value for field Batch in Sample form
    """
    adapts(IGetDefaultFieldValueARAddHook)

    def __call__(self, context):
        if IBatch.providedBy(context):
            return context

        # Try with batch explicitly defined in request
        return self.get_object_from_request_field("Batch")


class AddSampleClientInfo(AddSampleObjectInfoAdapter):
    """Returns the additional filter queries to apply when the value for the
    Client from Sample Add form changes
    """
    def get_object_info(self):
        object_info = self.get_base_info()

        # Apply filter for shareable types
        types = ["Patient", "Doctor", "Batch"]
        resolver = resolve_query_for_shareable
        filters = map(lambda st: (st, resolver(st, self.context)), types)
        object_info["filter_queries"] = dict(filters)
        return object_info


class AddSampleBatchInfo(AddSampleObjectInfoAdapter):
    """Returns the info metadata representation of a Batch object used in Add
    Sample form
    """
    def get_object_info(self):
        object_info = self.get_base_info()

        # Default values for other fields when the Batch is selected
        doctor = self.context.getField("Doctor").get(self.context)
        client = self.context.getClient()
        field_values = {
            "Doctor": self.to_field_value(doctor),
            "Client": self.to_field_value(client),
        }
        patient = self.context.getField("Patient").get(self.context)
        if patient:
            field_values.update({
                "Patient": self.to_field_value(patient),
                "ClientPatientID": {
                    "uid": api.get_uid(patient),
                    "title": patient.getClientPatientID() or api.get_id(patient),
                }
            })

        # Allow to choose Patients from same Client only and apply
        # generic filters when a client is selected too
        filter_queries = {}
        if client:
            query = {"query": api.get_path(client), "depth": 1}
            filter_queries = {
                "Patient": {"path": query},
                "ClientPatientID": {"path": query},
            }
        object_info["field_values"] = field_values
        object_info["filter_queries"] = filter_queries
        return object_info

    def to_field_value(self, obj):
        return {
            "uid": obj and api.get_uid(obj) or "",
            "title": obj and api.get_title(obj) or ""}


class AddSamplePatientInfo(AddSampleObjectInfoAdapter):
    """Returns the info metadata representation of a Patient object used in Add
    Sample form
    """
    def get_object_info(self):
        object_info = self.get_base_info()

        # Default values for other fields when the Patient is selected
        patient = self.context
        field_values = {
            "Patient": {
                "uid": api.get_uid(patient),
                "title": patient.getFullname(),
            },
            "ClientPatientID": {
                "uid": api.get_uid(patient),
                "title": patient.getClientPatientID() or "",
            }
        }
        object_info["field_values"] = field_values
        return object_info


class AddSampleFieldsFlush(object):
    """Health-specific flush of fields for Sample Add form. When the value for
    Client field changes, flush the fields "Patient", "Doctor" and "Batch"
    """
    adapts(IAddSampleFieldsFlush)

    def __init__(self, context):
        self.context = context

    def get_flush_settings(self):
        flush_settings = {
            "Client": [
                "Batch",
                "ClientPatientID",
                "Doctor",
                "Patient",
            ],
            "ClientPatientID": [
                "Patient",
            ],
            "Patient": [
                "ClientPatientID",
            ]
        }
        return flush_settings
