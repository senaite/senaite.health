from email.utils import formataddr
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.utils import encode_header
from bika.lims.browser.analysisrequest import InvoiceCreate as BaseClass
from bika.lims.browser.analysisrequest import InvoiceView as InvoiceViewLIMS


class InvoiceView(InvoiceViewLIMS):
    """ Rewriting the class to add the insurance company stuff in the invoice.
    """
    template = ViewPageTemplateFile("templates/analysisrequest_invoice.pt")
    print_template = ViewPageTemplateFile("templates/analysisrequest_invoice_print.pt")
    content = ViewPageTemplateFile("templates/analysisrequest_invoice_content.pt")

    def __call__(self):
        # Adding the insurance number variable to use in the template
        self.insurancenumber = self.context.Schema()['Patient'].get(self.context).getInsuranceNumber()
        return super(InvoiceView, self).__call__()

class InvoiceCreate(BaseClass):
    """
    A class extension to send the invoice to the insurance company.
    """

    def emailInvoice(self, templateHTML, to=[]):
        """
        Add the patient's insurance number in the receivers
        :param templateHTML: the html to render.
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
