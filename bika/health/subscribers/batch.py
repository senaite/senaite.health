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
from bika.health.utils import is_internal_client
from bika.health.utils import move_obj
from bika.lims import api
from bika.lims.interfaces import IClient


def ObjectCreatedEventHandler(batch, event):
    """A Batch (ClientCase) can be created inside Patient context. This
    function assign patient field automatically accordingly
    """
    if not batch.isTemporary():
        return

    parent = batch.getFolderWhenPortalFactory()
    if IPatient.providedBy(parent):
        # Assign the Patient to the Batch
        batch.getField("Patient").set(batch, parent)
        pid = parent.getClientPatientID()
        batch.getField("ClientPatientID").set(batch, pid)


def ObjectMovedEventHandler(batch, event):
    """Actions to be done when a Batch is added to a container. Moves the Batch
    to Client folder if assigned
    """
    if batch.isTemporary():
        return

    # We give priority to the assigned client over the Patient's client
    client = batch.getField("Client").get(batch)
    if not client:
        parent = batch.aq_parent
        if IClient.providedBy(parent):
            # The Batch belongs to an external client
            client = parent

        elif IPatient.providedBy(parent):
            # The Batch belongs to a Patient
            client = parent.getClient()

    if not client:
        # Batch belongs to the Lab
        # Batch is "lab private", only accessible by Lab Personnel
        move_to = api.get_portal().batches

    elif is_internal_client(client):
        # Batch belongs to an Internal Client
        # Batch is "shared", accessible to Internal Clients, but not to
        # external clients
        move_to = api.get_portal().batches

    else:
        # Batch belongs to an External Client.
        # Batch is "private", accessible to users from same client only
        move_to = client

    if move_to != batch.aq_parent:
        # Move the batch
        move_obj(batch, move_to)
