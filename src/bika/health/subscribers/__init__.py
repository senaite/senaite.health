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
from bika.health.utils import get_client_from_chain
from bika.health.utils import is_internal_client
from bika.lims import api
from bika.lims.interfaces import IClient
from bika.lims.workflow import doActionFor


def resolve_client(obj, field_name=None):
    """Tries to resolve the client for the given obj
    """
    if not field_name:
        field_name = "Client"
        if IPatient.providedBy(obj) or IDoctor.providedBy(obj):
            field_name = "PrimaryReferrer"

    # Try to get the client directly from the field
    client = obj.getField(field_name).get(obj)
    if client and IClient.providedBy(client):
        return client

    # Maybe the object is being created
    if obj.isTemporary():
        parent = obj.getFolderWhenPortalFactory()
    else:
        parent = api.get_parent(obj)

    # Get the Client from the acquisition chain, if any
    return get_client_from_chain(parent)


def try_share_unshare(obj):
    """Tries to share or unshare the object based on the type of its client
    """
    client = resolve_client(obj)
    if not IClient.providedBy(client):
        # This object does not (yet) have a client assigned, do nothing
        return

    if is_internal_client(client):
        # Try to share the obj. Note this transition will only take place if
        # the guard for "share" evaluates to True.
        doActionFor(obj, "share")
    else:
        # Try to unshare the obj. Note this transition will only take place
        # if the guard for "share" evaluates to True.
        doActionFor(obj, "unshare")
