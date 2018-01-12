# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser.client import ClientAnalysisRequestsView as BaseClientARView
from bika.health.browser.analysisrequests.view import AnalysisRequestsView as \
    HealthAnalysisRequestsView


class AnalysisRequestsView(BaseClientARView, HealthAnalysisRequestsView):

    def __call__(self):
        return super(AnalysisRequestsView, self).__call__()
