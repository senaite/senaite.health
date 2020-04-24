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

from bika.health.subscribers import resolve_client
from bika.health.utils import is_internal_client
from bika.health.utils import move_obj
from bika.lims import api
from bika.lims.api import security
from bika.lims.utils import changeWorkflowState


def ObjectCreatedEventHandler(patient, event):
    """This event assigns the value for the PrimaryReferrer field for Patient
    """
    if patient.isTemporary():
        # Only while object being created
        client = resolve_client(patient, field_name="PrimaryReferrer")
        patient.getField("PrimaryReferrer").set(patient, client)


def ObjectModifiedEventHandler(patient, event):
    """Actions to be done when a patient is modified. Moves the Patient to
    Client folder if assigned
    """
    # Move the patient if it does not match with the actual Client
    client = resolve_client(patient, field_name="PrimaryReferrer")
    if client != patient.aq_parent:
        patient = move_obj(patient, client)

    # Apply the proper workflow state (active/shared)
    wf_id = "senaite_health_patient_workflow"
    status = api.get_review_status(patient)
    internal = is_internal_client(client)

    if internal and status not in ["shared", "inactive"]:
        # Change to "shared" status, so all internal clients have access
        changeWorkflowState(patient, wf_id, "shared")

    elif not internal and status not in ["active", "inactive"]:
        # Change to "active" status, so only current client has access
        changeWorkflowState(patient, wf_id, "active")


# TODO: This is no longer needed!
def assign_owners_for(patient):
    """Assign the role "Owner" to the contacts of the client assigned to the
    patient passed in, if any
    """
    client = patient.getClient()
    if not client:
        return False

    contacts = client.objectValues("Contact")
    users = map(lambda contact: contact.getUser(), contacts)
    users = filter(None, users)
    for user in users:
        security.grant_local_roles_for(patient, roles=["Owner"], user=user)
    patient.reindexObjectSecurity()
    return True


def purge_owners_for(patient):
    """Remove role "Owner" from all those client contacts that do not belong to
    the same Client the patient is assigned to and assigns the role "Owner" to
    the client contacts assigned to the patient
    """
    # Add role "Owner" for this Patient to all contacts from this Client
    assign_owners_for(patient)

    # Unassign role "Owner" from contacts that belong to another Client
    patient_client = patient.getClient()
    patient_client_uid = patient_client and api.get_uid(patient_client) or None
    for client in api.search(dict(portal_type="Client"), "portal_catalog"):
        if api.get_uid(client) == patient_client_uid:
            continue

        client = api.get_object(client)
        contacts = client.objectValues("Contact")
        users = map(lambda contact: contact.getUser(), contacts)
        users = filter(None, users)
        for user in users:
            security.revoke_local_roles_for(patient, ["Owner"], user=user)
    patient.reindexObjectSecurity()
