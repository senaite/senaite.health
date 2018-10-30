# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.health import bikaMessageFactory as _
from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.browser.analysisrequest import AnalysisRequestsView


class AnalysisRequestsView(AnalysisRequestsView):

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
        client = self.context.getPrimaryReferrer()
        url = "{}/{}".format(api.get_url(client), "ar_add")
        qs = self.request.getHeader("query_string")
        if qs:
            url = "{}?{}".format(url, qs)
        self.request.response.redirect(url)
        return