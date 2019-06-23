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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.health.interfaces import IDoctor, IPatient
from bika.lims import api
from bika.lims.interfaces import IGetDefaultFieldValueARAddHook, IClient
from zope.component import adapts


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

        # Try with client object explicitly defined in request
        client = self.get_object_from_request_field("Client")
        if client:
            return client

        # Try to get the client from selected Patient
        patient = PatientDefaultFieldValue(self.request)(context)
        client = patient and patient.getPrimaryReferrer() or None
        if client:
            return client

        # Try to get the client from selected Doctor
        doctor = DoctorDefaultFieldValue(self.request)(context)
        client = doctor and doctor.getPrimaryReferrer() or None
        if client:
            return client

        return None



class PatientDefaultFieldValue(AddFormFieldDefaultValueAdapter):
    """Adapter that returns the default value for field Patien in Sample form
    """
    adapts(IGetDefaultFieldValueARAddHook)

    def __call__(self, context):
        if IPatient.providedBy(context):
            return context

        # Try with doctor explicitly defined in request
        return self.get_object_from_request_field("Patient")



class DoctorDefaultFieldValue(AddFormFieldDefaultValueAdapter):
    """Adapter that returns the default value for field Doctor in Sample form
    """
    adapts(IGetDefaultFieldValueARAddHook)


    def __call__(self, context):
        if IDoctor.providedBy(context):
            return context

        # Try with doctor explicitly defined in request
        return self.get_object_from_request_field("Doctor")
