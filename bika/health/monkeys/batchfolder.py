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

from bika.lims import AddBatch
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.api.security import check_permission
from bika.lims.browser.batchfolder import BatchFolderContentsView
from bika.lims.interfaces import IClient


# TODO Remove for compatibility with senaite.core v1.3.3
# Superseded by https://github.com/senaite/senaite.core/pull/1467
def update(self):
    """Before template render hook
    """
    super(BatchFolderContentsView, self).update()

    if self.context.portal_type == "BatchFolder":
        self.request.set("disable_border", 1)

    # By default, only users with AddBatch permissions for the current
    # context can add batches.
    self.context_actions = {
        _("Add"): {
            "url": "createObject?type_name=Batch",
            "permission": AddBatch,
            "icon": "++resource++bika.lims.images/add.png"
        }
    }

    # If current user is a client contact and current context is not a
    # Client, then modify the url for Add action so the Batch gets created
    # inside the Client object to which the current user belongs. The
    # reason is that Client contacts do not have privileges to create
    # Batches inside portal/batches
    if not IClient.providedBy(self.context):
        # Get the client the current user belongs to
        client = api.get_current_client()
        if client and check_permission(AddBatch, client):
            add_url = self.context_actions[_("Add")]["url"]
            add_url = "{}/{}".format(api.get_url(client), add_url)
            self.context_actions[_("Add")]["url"] = add_url
            del (self.context_actions[_("Add")]["permission"])


# TODO Remove for compatibility with senaite.core v1.3.3
# Superseded by https://github.com/senaite/senaite.core/pull/1467
def before_render(self):
    """Before template render hook
    """
    super(BatchFolderContentsView, self).before_render()
