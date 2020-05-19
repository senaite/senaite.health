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
            field_name = "ChronicConditions"

            # Get the field
            field = self.context.getField(field_name)

            # Get the form values submitted for this field
            conditions = self.request.form.get(field_name)

            # Validate sub_field values
            valid = map(lambda c: self.validate(field, c), conditions)
            if all(valid):
                # All chronic conditions are correct
                self.context.setChronicConditions(conditions)
                self.context.plone_utils.addPortalMessage(_p("Changes saved"))

            elif valid:
                # With at least one item, but not correct
                self.context.plone_utils.addPortalMessage(
                    _p("Please correct the indicated errors"), "error")

        return self.template()

    def validate(self, field, condition):
        """Returns True if all required values for the condition are valid
        """
        required = field.required_subfields
        types = field.subfield_types

        for subfield in required:
            typ = types.get(subfield) or ""
            val = condition.get(subfield)
            val = val and val.strip()
            if "date" in typ:
                if not api.to_date(val, default=None):
                    # Not a valid date
                    return False
            elif not val:
                # Not a valid value
                return False

        # All checks passed
        return True
