# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.health.browser.samples.folder_view import SamplesView
from Products.CMFCore.utils import getToolByName


class SamplesView(SamplesView):

    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)
        self.contentFilter['Doctor'] = self.context.UID()

    def contentsMethod(self, contentFilter):
        tool = getToolByName(self.context, self.catalog)
        state = [x for x in self.review_states if x['id'] == self.review_state['id']][0]
        for k, v in state['contentFilter'].items():
            self.contentFilter[k] = v
        tool_samples = tool(contentFilter)
        samples = {}
        for sample in (p.getObject() for p in tool_samples):
            for ar in sample.getAnalysisRequests():
                if ar['Doctor'] == self.context.UID():
                    samples[sample.getId()] = sample
        return samples.values()
