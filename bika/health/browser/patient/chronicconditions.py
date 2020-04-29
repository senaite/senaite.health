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
from bika.lims import api
from bika.lims.browser import BrowserView


class ChronicConditionsView(BrowserView):
    template = ViewPageTemplateFile("chronicconditions.pt")

    def __call__(self):
        if 'submitted' in self.request:

            conditions = self.request.form.get("ChronicConditions")

            # Check if all required items have been filled
            valid = map(self.validate, conditions)
            if all(valid):
                # All chronic conditions are correct
                self.context.setChronicConditions(conditions)
                self.context.plone_utils.addPortalMessage(_p("Changes saved"))

            elif valid:
                # With at least one item, but not correct
                self.context.plone_utils.addPortalMessage(
                    _p("Please correct the indicated errors"), "error")

        return self.template()

    def validate(self, condition):
        """Returns True if all required values for the condition are valid
        """
        title = condition.get("Title")
        title = title and title.strip()
        if not title:
            # Not a valid title
            return False

        onset = condition.get("Onset")
        if not api.to_date(onset, default=None):
            # Not a valid Onset date
            return False

        return True
