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
from bika.health.utils import is_from_external
from bika.health.utils import is_internal_client
from bika.lims.adapters.widgetvisibility import SenaiteATWidgetVisibility
from bika.lims.interfaces import IClient
from bika.health import logger
from bika.lims import api


class ClientFieldVisibility(SenaiteATWidgetVisibility):
    """Handles the Client field visibility in Doctor context
    """

    def __init__(self, context):
        super(ClientFieldVisibility, self).__init__(
            context=context, field_names=["PrimaryReferrer"])

    def isVisible(self, field, mode="view", default="visible"):
        """Renders the Client field as hidden if the current mode is "edit" and
        the Doctor has Batches or Samples assigned already
        """
        if mode == "edit":
            container = self.context.aq_parent
            if IClient.providedBy(container):
                # This Doctor belongs to an external client
                return "invisible"

            if self.context.getBatches() or self.context.getSamples():
                # Maybe the Doctor does not have any Client assigned, so give
                # the option to at least assign an internal client if all the
                # samples and batches are from internal clients
                client = self.context.getClient()
                if not client or is_internal_client(client):
                    # Try with Batches first
                    ext = filter(is_from_external, self.context.getBatches())
                    if ext:
                        return "readonly"

                    # Try with Samples
                    ext = filter(is_from_external, self.context.getSamples())
                    if ext:
                        return "readonly"

                    # Seems this Doctor does not have any Sample/Batch assigned
                    # Allow to modify the Client
                    return default

                # Not inside a Client context. Display the client at least
                return "readonly"

        return default
