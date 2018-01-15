# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.health.browser.samples.folder_view import SamplesView


class ClientSamplesView(SamplesView):
    """ Overrides bika.lims.browser.client.ClientSamplesView
        through bika.health.browser.samples.folder_view.SamplesView
        Add columns with information about the patient
    """
    def __init__(self, context, request):
        super(ClientSamplesView, self).__init__(context, request)
        self.contentFilter['path'] = {"query": "/".join(context.getPhysicalPath()),
                                      "level": 0}
        # review_states = []
        # for review_state in self.review_states:
        #     review_state['columns'].remove('Client')
        #     review_states.append(review_state)
        # self.review_states = review_states
