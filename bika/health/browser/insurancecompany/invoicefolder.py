from bika.lims.browser.invoicefolder import InvoiceFolderContentsView


class InvInvoiceFolderContentsView(InvoiceFolderContentsView):

    def __init__(self, context, request):
        super(InvoiceFolderContentsView, self).__init__(context, request)