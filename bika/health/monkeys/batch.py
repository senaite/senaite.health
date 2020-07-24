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
from bika.health.utils import is_from_external_client
from bika.lims.interfaces import IClient


def getClient(self):
    """Returns the Client from the Batch passed-in, if any
    """
    parent = self.aq_parent
    if IClient.providedBy(parent):
        # The Batch belongs to an External Client
        return parent

    elif IPatient.providedBy(parent) and is_from_external_client(parent):
        # The Batch belongs to a Patient
        return parent.getClient()

    parent = self.getField("Client").get(self)
    if parent:
        # The Batch belongs to an Internal Client, either because is directly
        # assigned to the Client or because belongs to a Patient from an
        # internal client
        return parent

    # The Batch belongs to the laboratory (no Client assigned)
    return None
