# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.health.browser.samples.folder_view import SamplesView as BaseView
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING


class SamplesView(BaseView):

    def __call__(self):
        self.remove_column('getDoctor')
        self.contentFilter['UID'] = self.get_sample_uids()
        return super(SamplesView, self).__call__()

    def get_sample_uids(self):
        """Returns the sample UIDs for which the current Doctor has at least
        one Analysis Request assigned."""
        query = dict(getDoctorUID=api.get_uid(self.context))
        ars = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
        uids = map(lambda brain: brain.getSampleUID, ars) or list()
        return list(set(uids))
