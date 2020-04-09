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

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import PMF as _p
from bika.lims.browser import BrowserView


class TreatmentHistoryView(BrowserView):
    template = ViewPageTemplateFile("treatmenthistory.pt")

    def __call__(self):
        if 'submitted' in self.request:
            self.context.setTreatmentHistory(self.request.form.get('TreatmentHistory', ()))
            self.context.plone_utils.addPortalMessage(_p("Changes saved"))
        return self.template()
