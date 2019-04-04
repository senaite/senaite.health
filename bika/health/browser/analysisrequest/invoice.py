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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from email.utils import formataddr
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.utils import encode_header
from bika.lims.browser.analysisrequest import InvoiceCreate as BaseClass
from bika.lims.browser.analysisrequest import InvoiceView as InvoiceViewLIMS
from bika.lims.browser.analysisrequest import InvoicePrintView as InvoicePrintViewLIMS


class InvoiceView(InvoiceViewLIMS):
    """ Rewriting the class to add the insurance company stuff in the invoice.
    """
    # We need to load the templates from health
    template = ViewPageTemplateFile("templates/analysisrequest_invoice.pt")
    content = ViewPageTemplateFile("templates/analysisrequest_invoice_content.pt")

    def __call__(self):
        # Adding the insurance number variable to use in the template
        self.insurancenumber = self.context.Schema()['Patient'].get(self.context).getInsuranceNumber()
        return super(InvoiceView, self).__call__()


class InvoicePrintView(InvoiceView):
    # We need to load the template from health.
    template = ViewPageTemplateFile("templates/analysisrequest_invoice_print.pt")

    def __call__(self):
        return InvoiceView.__call__(self)

class InvoiceCreate(BaseClass):
    """
    A class extension to send the invoice to the insurance company.
    """
    print_template = ViewPageTemplateFile("templates/analysisrequest_invoice_print.pt")
    content = ViewPageTemplateFile("templates/analysisrequest_invoice_content.pt")

    def __call__(self):
        self.insurancenumber = self.context.Schema()['Patient'].get(self.context).getInsuranceNumber()
        BaseClass.__call__(self)

    def emailInvoice(self, templateHTML, to=[]):
        """
        Add the patient's insurance number in the receivers
        :param templateHTML: the html to render. We override it.
        :param to: the list with the receivers. Void in this case.
        """
        # Check if the patient's "Send invoices to the insurance company" checkbox is checked.
        sendtoinsurance = self.context.Schema()['Patient'].get(self.context).getInvoiceToInsuranceCompany()
        if sendtoinsurance:
            # Obtains the insurance company object
            insurancecompany = self.context.Schema()['Patient'].get(self.context).getInsuranceCompany()
            # Build the insurance company's address
            icaddress = insurancecompany.getEmailAddress()
            icname = insurancecompany.getName()
            if (icaddress != ''):
                    to.append(formataddr((encode_header(icname), icaddress)))
        super(InvoiceCreate, self).emailInvoice(templateHTML, to)
