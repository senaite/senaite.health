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

from bika.health import bikaMessageFactory as _
from bika.health.utils import is_internal_client
from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.browser.analysisrequest import AnalysisRequestsView as BaseView


class AnalysisRequestsView(BaseView):

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.contentFilter['getPatientUID'] = self.context.UID()
        self.show_all = True
        self.columns['BatchID']['title'] = _('Case ID')


class AnalysisRequestAddRedirectView(BrowserView):
    """Artifact to redirect the user to AR Add view when 'AR Add' button is
    clicked in Patient's Analysis Requests view
    """

    def __call__(self):
        client = self.context.getClient()
        if not client:
            # Patient from the laboratory (no client assigned)
            base_folder = api.get_portal().analysisrequests
        elif is_internal_client(client):
            # Patient from an internal client, shared
            base_folder = api.get_portal().analysisrequests
        else:
            # Patient from an external client, private
            base_folder = client

        url = "{}/{}".format(api.get_url(base_folder), "ar_add")
        url = "{}?Patient={}".format(url, api.get_uid(self.context))
        qs = self.request.getHeader("query_string")
        if qs:
            url = "{}&{}".format(url, qs)
        return self.request.response.redirect(url)
