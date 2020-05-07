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

from plone.app.layout.viewlets import ViewletBase

from bika.health.utils import is_internal_client
from bika.lims import api


class ClientTypeViewlet(ViewletBase):
    """Display a message stating whether Patients, Batches and Doctors are
    shared (the client is internal) or not (the client is external)
    """

    def is_visible(self):
        """Returns whether the viewlet must be visible or not
        """
        logged_client = api.get_current_client()
        if not logged_client:
            # Current user is from Lab, display always
            return True

        # Only display the viewlet if the current user does belong to an
        # Internal Client. It does not make sense to display this viewlet if
        # the user is from an external client, cause in such case, there is no
        # need to warn him/her. He/She expects that their own Patients, Cases
        # and Doctors are private already
        return is_internal_client(logged_client)

    def is_internal(self):
        """Returns whether the current client is internal or not
        """
        return is_internal_client(self.context)
