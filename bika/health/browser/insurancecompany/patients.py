# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.health.browser.patients.folder_view import PatientsView as BaseView
from bika.lims import api


class PatientsView(BaseView):

    def isItemAllowed(self, obj):
        # TODO: Performance tip. We need the full object to filter by Insurance
        uid = api.get_uid(self.context)
        full_obj = api.get_object(obj)
        insurance_company = full_obj.getInsuranceCompany()
        if not insurance_company:
            return False
        return api.get_uid(insurance_company) == uid
