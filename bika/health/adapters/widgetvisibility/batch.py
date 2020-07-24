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

from bika.health.interfaces import IDoctor
from bika.health.interfaces import IPatient
from bika.health.utils import is_from_external_client
from bika.lims.adapters.widgetvisibility import SenaiteATWidgetVisibility
from bika.lims.interfaces import IClient


class ClientFieldVisibility(SenaiteATWidgetVisibility):
    """Handles the Client field visibility in Batch context
    """

    def __init__(self, context):
        super(ClientFieldVisibility, self).__init__(
            context=context, field_names=["Client"])

    def isVisible(self, field, mode="view", default="visible"):
        """Renders the Client field as hidden if the current mode is "edit" and
        the container is a Patient that belongs to an external client or when
        the container is a Client. If the container is a Patient that belongs to
        an internal client, the field is kept editable, cause user might want to
        assign the batch to an internal client other than the current one.
        """
        if mode == "edit":
            container = self.context.aq_parent

            # If the Batch is created or edited inside a Client, Patient or
            # Doctor make Client field to be rendered, but hidden to prevent
            # the error message "Patient is required, please correct".
            if IPatient.providedBy(container):
                # User might want to assign the batch to an internal client
                # other than the Patient's
                if is_from_external_client(container):
                    return "readonly"

            elif IClient.providedBy(container):
                return "readonly"

            elif IDoctor.providedBy(container):
                # Doctor can be assigned to a Client or not!
                if container.getClient():
                    return "readonly"

        return default


class PatientFieldsVisibility(SenaiteATWidgetVisibility):
    """Handles the visibility of Patient and ClientPatientID fields
    """

    def __init__(self, context):
        super(PatientFieldsVisibility, self).__init__(
            context=context, sort=10, field_names=["Patient"])

    def isVisible(self, field, mode="view", default="visible"):
        """Renders Patient and ClientPatientID fields as hidden if the current
        mode is "edit" and the the container is a Patient or if the Batch has
        a Patient already assigned (do not allow the modification of Patient)
        """
        if mode == "edit":
            container = self.context.aq_parent
            if IPatient.providedBy(container):
                return "readonly"

            # Do not allow the edition of Patient if assigned already
            patient = self.context.getField("Patient").get(self.context)
            if patient:
                return "readonly"

        return default


class DoctorFieldVisibility(SenaiteATWidgetVisibility):
    """Handles the Doctor field visibility in Batch context
    """

    def __init__(self, context):
        super(DoctorFieldVisibility, self).__init__(
            context=context, field_names=["Doctor"])

    def isVisible(self, field, mode="view", default="visible"):
        """Renders the Doctor field as hidden if the current mode is "edit" and
        the container is a Doctor
        """
        if mode == "edit":
            container = self.context.aq_parent
            if IDoctor.providedBy(container):
                # Doctor can be assigned to a Client or not!
                if container.getClient():
                    return "readonly"

        return default

