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

from bika.health import logger
from bika.health.utils import move_obj
from bika.lims import api
from bika.lims.api import security


def ObjectModifiedEventHandler(patient, event):
    """Actions to be done when a patient is modified. Moves the Patient to
    Client folder if assigned
    """
    move_to = patient.aq_parent
    primary_referrer = patient.getField("PrimaryReferrer").get(patient)

    if not primary_referrer:
        # Patient belongs to the Lab.
        # Patient is "lab private", only accessible by Lab Personnel
        move_to = api.get_portal().patients

    elif primary_referrer:
        # Check if the primary referrer is an Internal or an External Client
        external_clients = api.get_portal().clients
        internal_clients = api.get_portal().internal_clients

        if primary_referrer.aq_parent == internal_clients:
            # Patient belongs to an Internal Client.
            # Patient is "shared", accessible to Internal Clients, but not to
            # External Clients
            move_to = api.get_portal().patients

        elif primary_referrer.aq_parent == external_clients:
            # Patient belongs to an External Client.
            # Patient is "private", accessible to users from same Client only
            move_to = primary_referrer

        else:
            logger.error("Not a valid Primary Referrer for {}: {}".format(
                api.get_id(patient), api.get_path(move_to)
            ))

    if move_to != patient.aq_parent:
        # Move the patient
        move_obj(patient, move_to)


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
