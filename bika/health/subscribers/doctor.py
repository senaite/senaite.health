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

from bika.health.interfaces import IDoctors
from bika.health.utils import is_internal_client
from bika.health.utils import move_obj
from bika.lims import api
from bika.lims.interfaces import IClient
from bika.lims.utils import changeWorkflowState


def ObjectModifiedEventHandler(doctor, event):
    """Actions to be done when a doctor is modified. Moves the Doctor to the
    Client folder if the assigned client is an external. Moves the Doctor to
    the base /doctors folder otherwise
    """
    client = doctor.getField("PrimaryReferrer").get(doctor)
    if not client:
        client = doctor.getClient()
        if client:
            # The Doctor is being created inside a Client folder, so the
            # PrimaryReferrer field comes empty (the field is hidden when the
            # Doctor Add/Edit form is rendered inside a Client context)
            doctor.getField("PrimaryReferrer").set(doctor, client)

    if not client:
        # Doctor belongs to the Lab.
        # Doctor is "lab private", only accessible by Lab Personnel
        move_to = api.get_portal().doctors

    elif is_internal_client(client):
        # Doctor belongs to an Internal Client.
        # Doctor is "shared", accessible to Internal Clients, but not to
        # External Clients
        move_to = api.get_portal().doctors

    else:
        # Doctor belongs to an External Client.
        # Doctor is "private", accessible to users from same Client only
        move_to = client

    if move_to != doctor.aq_parent:
        # Move the doctor
        move_obj(doctor, move_to)

    # Apply the proper workflow state (active/shared)
    wf_id = "senaite_health_doctor_workflow"
    status = api.get_review_status(doctor)
    if status not in ["shared", "inactive"] and IDoctors.providedBy(move_to):
        changeWorkflowState(doctor, wf_id, "shared")
    elif status not in ["active", "inactive"] and IClient.providedBy(move_to):
        changeWorkflowState(doctor, wf_id, "active")
