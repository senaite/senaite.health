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

from bika.health.interfaces import IPatient
from bika.health.utils import set_field_value


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
        batch.getField("ClientPatientID").set(batch, parent)

        # Assign the client from the patient too
        set_field_value(batch, "Client", parent.getClient())
