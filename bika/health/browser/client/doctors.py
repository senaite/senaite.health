# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.health.browser.doctors.folder_view import DoctorsView


class ClientDoctorsView(DoctorsView):

    def __init__(self, context, request):
        DoctorsView.__init__(self, context, request)

        # Limit results to those patients that "belong" to this client
        self.contentFilter['getPrimaryReferrerUID'] = context.UID()
