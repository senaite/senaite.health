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
from bika.health import utils
from bika.lims.browser.analysisrequest import InvoiceCreate as BaseInvoiceCreate
from bika.lims.browser.analysisrequest import \
    InvoicePrintView as BaseInvoicePrintView
from bika.lims.browser.analysisrequest import InvoiceView as BaseInvoiceView


class InvoiceView(BaseInvoiceView):
    """ Rewriting the class to add the insurance company stuff in the invoice.
    """
    content = ViewPageTemplateFile("templates/analysisrequest_invoice_content.pt")

    @property
    def insurance_number(self):
        """Returns the Patient's insurance number
        """
        return utils.get_field_value(self.context, "InsuranceNumber", "")


class InvoicePrintView(BaseInvoicePrintView):

    content = ViewPageTemplateFile("templates/analysisrequest_invoice_content.pt")

    @property
    def insurance_number(self):
        """Returns the Patient's insurance number
        """
        return utils.get_field_value(self.context, "InsuranceNumber", "")


class InvoiceCreate(BaseInvoiceCreate):

    content = ViewPageTemplateFile("templates/analysisrequest_invoice_content.pt")

    @property
    def insurance_number(self):
        """Returns the Patient's insurance number
        """
        return utils.get_field_value(self.context, "InsuranceNumber", "")
