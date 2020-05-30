# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH.
#
# SENAITE.HEALTH is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

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
