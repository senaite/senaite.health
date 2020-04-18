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

from senaite.core.listing.interfaces import IListingView
from senaite.core.listing.interfaces import IListingViewAdapter
from zope.component import adapts
from zope.interface import implements

from bika.lims import api


class ClientsListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        # Use the title of the containing folder
        title = api.get_title(self.context)
        self.listing.title = self.context.translate(title)

        # Use the icon of the containing folder
        icon = self.context.icon().replace(".png", "_big.png")
        self.listing.icon = "{}/{}".format(self.listing.portal_url, icon)

        # Display clients that belong to current folder only
        self.listing.contentFilter.update({
            "path": {
                "query": api.get_path(self.context),
                "depth": 1
            },
        })

    def folder_item(self, obj, item, index):
        return item