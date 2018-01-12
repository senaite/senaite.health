# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
