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

from bika.lims import api
from bika.lims.adapters.widgetvisibility import SenaiteATWidgetVisibility


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
            client = self.context.getClient()
            if client == api.get_parent(self.context):
                # We are already inside the parent's context
                return "hidden"

            elif client:
                # We are in another context, read-only
                return "readonly"

        return default
