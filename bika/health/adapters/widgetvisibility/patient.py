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

from bika.lims.adapters.widgetvisibility import SenaiteATWidgetVisibility
from bika.lims.interfaces import IClient


class ClientFieldVisibility(SenaiteATWidgetVisibility):
    """Handles the Client (PrimaryReferrer) field visibility in Patient context
    """

    def __init__(self, context):
        super(ClientFieldVisibility, self).__init__(
            context=context, field_names=["PrimaryReferrer"])

    def isVisible(self, field, mode="view", default="visible"):
        """Renders the PrimaryReferrer field (Client) as readonly when the
        mode is "edit" and the container is a Client
        """
        if mode == "edit":
            container = self.context.aq_parent
            if IClient.providedBy(container):
                return "readonly"

        return default
