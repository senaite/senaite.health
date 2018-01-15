# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.health.browser.analysisrequests.view import AnalysisRequestsView as BaseView


class AnalysisRequestsView(BaseView):
    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.contentFilter['getDoctorUID'] = self.context.UID()
