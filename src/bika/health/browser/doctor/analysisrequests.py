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

from bika.health.browser.analysisrequests.view import \
    AnalysisRequestsView as BaseView
from bika.lims import api
from bika.lims.browser import BrowserView


class AnalysisRequestsView(BaseView):

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.contentFilter['getDoctorUID'] = self.context.UID()



class AnalysisRequestAddRedirectView(BrowserView):
    """Artifact to redirect the user to AR Add view when 'AR Add' button is
    clicked in Doctor's Analysis Requests view
    """

    def __call__(self):
        base_folder = self.context.getPrimaryReferrer()
        if not base_folder:
            # Doctor w/o client assigned, just use analysisrequests folder
            base_folder = api.get_portal().analysisrequests

        url = "{}/{}".format(api.get_url(base_folder), "ar_add")
        url = "{}?Doctor={}".format(url, api.get_uid(self.context))
        qs = self.request.getHeader("query_string")
        if qs:
            url = "{}&{}".format(url, qs)
        return self.request.response.redirect(url)
