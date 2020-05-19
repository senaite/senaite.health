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
from bika.health.subscribers import try_share_unshare
from bika.health.utils import move_obj


def ObjectCreatedEventHandler(patient, event):
    """Actions done when a patient is created. Automatically assigns the
    value for "PrimaryReferrer" (Client) field
    """
    if patient.isTemporary():
        # Only while object being created
        client = resolve_client(patient, field_name="PrimaryReferrer")
        patient.getField("PrimaryReferrer").set(patient, client)


def ObjectModifiedEventHandler(patient, event):
    """Actions to be done when a patient is modified. Moves the Patient to the
    Client folder and transitions to "shared" or "active" when necessary
    """
    # Move the patient if it does not match with the actual Client
    client = resolve_client(patient, field_name="PrimaryReferrer")
    if client != patient.aq_parent:
        patient = move_obj(patient, client)

    # Try to share/unshare the patient based on its type of Client
    try_share_unshare(patient)
