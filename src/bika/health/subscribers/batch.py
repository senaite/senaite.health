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
from bika.health.subscribers import resolve_client
from bika.health.subscribers import try_share_unshare
from bika.lims.interfaces import IClient


def ObjectCreatedEventHandler(case, event):
    """Actions done when a Batch (Clinic Case) is created. Automatically assigns
    value for "PrimaryReferrer" (Client), "Patient" and "Doctor" fields
    """
    if case.isTemporary():
        # Assign client
        client = resolve_client(case, field_name="Client")
        case.getField("Client").set(case, client)

        # Assign the Patient
        parent = case.getFolderWhenPortalFactory()
        if IPatient.providedBy(parent):
            # Batch is being created inside a Patient
            cpid = parent.getClientPatientID()
            case.getField("Patient").set(case, parent)
            case.getField("ClientPatientID").set(case, cpid)

        elif IDoctor.providedBy(parent):
            # Batch is being created inside a Doctor
            case.getField("Doctor").set(case, parent)


def ObjectModifiedEventHandler(case, event):
    """Actions to be done when a Batch is modified. Transitions the case to
    "shared" or "open" when necessary

    There is an ObjectModifiedEventHandler registered at senaite.core already,
    that always moves the Batch to the Client folder. Therfore, this handler
    can be called "before" the call in "core" or "after" the call in core.
    """
    # Object being created
    if case.isTemporary() or case.checkCreationFlag():
        return

    if not IClient.providedBy(case.aq_parent):
        # Let core's default ObjectModifiedEvent deal with it, we will "trap"
        # his modif later in ObjectMovedEventHandler
        return

    # Try to share/unshare the batch based on its type of Client
    try_share_unshare(case)


def ObjectMovedEventHandler(case, event):
    """Actions to be done when a Batch is modified. Transitions the case to
    "shared" or "active" when necessary

    This event is necessary because in senaite.core there is an
    ObjectModifiedEventHandler registered for type Batch already, that always
    moves the Batch to the client folder. Therefore we also need these event to
    "trap" when the object is moved to a Client by core's event.
    """
    # Object being created
    if case.isTemporary() or case.checkCreationFlag():
        return

    # Do nothing if only the title changes
    if event.oldName != event.newName:
        return

    # Try to share/unshare the batch based on its type of Client
    try_share_unshare(case)
