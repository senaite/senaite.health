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

from bika.health.utils import is_internal_client
from bika.lims import api
from bika.lims.interfaces import IClient
from bika.lims.utils import chain
from bika.lims.utils import changeWorkflowState


def resolve_client(obj, field_name="Client"):
    """Tries to resolve the client for the given Patient
    """
    client = obj.getField(field_name).get(obj)
    if client and IClient.providedBy(client):
        return client

    # Maybe the object is being created
    if obj.isTemporary():
        parent = obj.getFolderWhenPortalFactory()
        if IClient.providedBy(parent):
            return parent

    # Try to get the Client from the acquisition chain
    for parent in chain(obj):
        if api.is_object(parent) and IClient.providedBy(parent):
            return parent

    # Cannot resolve
    return None


def try_share(obj, wf_id):
    """Returns whether the object passed-in is shareable by looking
    at the type of client it belongs to
    """
    status = api.get_review_status(obj)
    internal = is_internal_client(obj.getClient())
    if internal and status not in ["shared", "inactive"]:
        # Change to "shared" status, so all internal clients have access
        changeWorkflowState(obj, wf_id, "shared")

    elif not internal and status not in ["active", "inactive"]:
        # Change to "active" status, so only current client has access
        changeWorkflowState(obj, wf_id, "active")
