# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.health.browser.patients.folder_view import PatientsView


class ClientPatientsView(PatientsView):

    def __init__(self, context, request):
        super(ClientPatientsView, self).__init__(context, request)

        # Limit results to those patients that "belong" to this client
        self.contentFilter['getPrimaryReferrerUID'] = context.UID()

    def _initFormParams(self):
        super(ClientPatientsView, self)._initFormParams()

        # Remove PrimaryReferrerTitle column
        self.remove_column('getPrimaryReferrerTitle')
