# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.health.browser.samples.folder_view import SamplesView


class BatchSamplesView(SamplesView):

    def __init__(self, context, request):
        super(BatchSamplesView, self).__init__(context, request)
        self.view_url = self.context.absolute_url() + "/samples"
        self.contentFilter = {'portal_type': 'Sample',
                              'getBatchUIDs': api.get_uid(self.context),
                              'sort_on': 'created',
                              'sort_order': 'reverse',
                              'cancellation_state':'active'}
