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

from bika.health.interfaces import IPatient
from bika.lims.adapters.widgetvisibility import SenaiteATWidgetVisibility
from bika.lims.interfaces import IBatch


class DoctorFieldVisibility(SenaiteATWidgetVisibility):
    """Handles Doctor field visibility in Sample add form and view
    """

    def __init__(self, context):
        super(DoctorFieldVisibility, self).__init__(
            context=context, sort=10, field_names=["Doctor"])

    def isVisible(self, field, mode="view", default="visible"):
        if mode == "add":
            container = self.context.aq_parent

            # Do not display the doctor field if the Sample is being created
            # inside a Batch and the latter has a Doctor assigned. In such
            # case, the batch assigned to the Batch will be used:
            # See: adapters.addsample.DoctorDefaultFieldValue
            if IBatch.providedBy(container):
                doctor = container.getField("Doctor").get(container)
                if doctor:
                    return "hidden"

        return default


class PatientFieldsVisibility(SenaiteATWidgetVisibility):
    """Handles "Batch", "Patient" and "ClientPatientID" fields visibility in
    Sample (Analysis Request) context. They are not editable, regardless of the
    current state of the Sample, except when displayed in AR Add view. The
    reason is that all these fields, together with Client field, are strongly
    related.
    """
    def __init__(self, context):
        super(PatientFieldsVisibility, self).__init__(
            context=context, sort=10,
            field_names=["Batch", "Patient", "ClientPatientID", ])

    def isVisible(self, field, mode="view", default="visible"):
        if mode == "edit":
            return "invisible"

        elif mode == "add":
            container = self.context.aq_parent

            # Do not display the Patient field if the Sample is being created
            # inside a Batch and the latter has a Patient assigned. In such
            # case, the patient assigned to the Batch will be used:
            # See: adapters.addsample.PatientDefaultFieldValue
            if IBatch.providedBy(container):
                patient = container.getField("Patient").get(container)
                if patient:
                    return "hidden"

        return default
