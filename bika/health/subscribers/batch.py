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

    elif IClient.providedBy(parent):
        # Assign the client. When the Batch is being created inside a Client
        # folder directly, the field Client is not visible (see adapter for
        # widgetvisibility) and therefore, not considered in processForm
        batch.getField("Client").set(batch, api.get_uid(parent))


def ObjectModifiedEventHandler(batch, event):
    """Actions to be done when a Batch is modified. Moves the Batch to the
    base Batches folder if the batch is assigned to an internal client. If
    external client, it moves the Batch the Client folder
    """
    # Object being created
    if batch.isTemporary() or batch.checkCreationFlag():
        return

    if IPatient.providedBy(batch.aq_parent):
        # Let core's default ObjectModifiedEvent deal with it
        return

    # Move the Batch
    move_batch(batch)


def ObjectMovedEventHandler(batch, event):
    """Actions to be done when a Batch is modified. Moves the Batch to the
    base Batches folder if the batch is assigned to an internal client. If
    external client, it moves the Batch the Client folder

    This event is necessary because in senaite.core there is an ObjectMovedEvent
    registered for type Batch already that always moves the Batch to the client
    folder. Therefore we also need these event to "trap" when the object is
    moved by core's ObjectModified event.
    """
    # Object being created
    if batch.isTemporary() or batch.checkCreationFlag():
        return

    # Do nothing if only the title changes
    if event.oldName != event.newName:
        return

    # Move the batch
    move_batch(batch)


def move_batch(batch):
    """Moves the Batch to the base Batches folder if the batch is assigned to
    an internal client. If external client, it moves the Batch the Client folder
    """
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

    prev_parent = batch.aq_parent
    if move_to != prev_parent:
        # Move the batch
        move_obj(batch, move_to)

        # Assign the client. When the Batch is being created inside a Client
        # folder directly, the field Client is not visible (see adapter for
        # widgetvisibility) and therefore, not considered in processForm
        if IClient.providedBy(prev_parent):
            batch.getField("Client").set(batch, api.get_uid(prev_parent))
