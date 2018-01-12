# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser.batch.analysisrequests import AnalysisRequestsView as BaseBatchARView
from bika.health.browser.analysisrequests.view import AnalysisRequestsView as \
    HealthAnalysisRequestView


class BatchAnalysisRequestsView(BaseBatchARView, HealthAnalysisRequestView):

    def __call__(self):
        return super(BatchAnalysisRequestsView, self).__call__()

    def __init__(self, context, request):
        super(BatchAnalysisRequestsView, self).__init__(context, request)
        self.columns['BatchID']['toggle'] = False
