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

from bika.health.browser.batchfolder import BatchListingViewAdapter
from bika.health.interfaces import IPatient
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.permissions import AddBatch


class PatientBatchListingViewAdapter(BatchListingViewAdapter):

    def before_render(self):
        """Called before the listing renders
        """
        super(PatientBatchListingViewAdapter, self).before_render()

        # Hide patient columns
        self.listing.columns['getPatientID']['toggle'] = False
        self.listing.columns['getClientPatientID']['toggle'] = False
        self.listing.columns['Patient']['toggle'] = False

        # Filter by patient
        query = dict(getPatientUID=api.get_uid(self.context))
        self.listing.contentFilter.update(query)
        for rv in self.listing.review_states:
            if "contentFilter" not in rv:
                rv["contentFilter"] = {}
            rv["contentFilter"].update(query)

        url = api.get_url(self.context)
        self.listing.context_actions = {
            _("Add"): {
                "url": "{}/createObject?type_name=Batch".format(url),
                "permission": AddBatch,
                "icon": "++resource++bika.lims.images/add.png"
            }
        }
