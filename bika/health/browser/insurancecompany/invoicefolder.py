from zope.interface.declarations import implements
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import currency_format


from bika.lims.permissions import AddInvoice
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _

""" This file contains a invoice type folder to be used in insurance company's stuff.
"""

class InvoiceFolderView(BikaListingView):
    implements(IFolderContentsView, IViewView)  # Why??

    def __init__(self, context, request):
        super(InvoiceFolderView, self).__init__(context, request)
        self.catalog = 'portal_catalog'
        self.contentFilter = {'portal_type': 'Invoice',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.title = self.context.translate(_("Invoices"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/invoice_big.png"
        self.description = "The invoices of Insurance Company's patients"
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.contentsMethod = False
        self.pagesize = 25
        self.columns = {
            'id': {'title': _('Invoice Number'),
                   'toggle': True},
            'client': {'title': _('Client'),
                       'toggle': True},
            'invoicedate': {'title': _('Invoice Date'),
                            'toggle': True},
            'subtotal': {'title': _('Subtotal')},
            'vatamount': {'title': _('VAT')},
            'total': {'title': _('Total')},
            'patient': {'title': _('Patient'),
                        'toggle': True},
        }
        self.review_states = [
            {
                'id': 'default',
                'contentFilter': {},
                'title': _('Default'),
                'transitions': [],
                'columns': [
                    'id',
                    'client',
                    'invoicedate',
                    'subtotal',
                    'vatamount',
                    'total',
                ],
            },
        ]

    def getInvoices(self, contentFilter):
        return self.context.objectValues('Invoice')

    def folderitems(self, full_objects = False):
        currency = currency_format(self.context, 'en')
        self.contentsMethod = self.getInvoices
        items = BikaListingView.folderitems(self)
        for item in items:
            obj = item['obj']
            number_link = "<a href='%s'>%s</a>" % (
                item['url'], obj.getId()
            )
            item['replace']['id'] = number_link
            item['client'] = obj.getClient().Title()
            item['invoicedate'] = self.ulocalized_time(obj.getInvoiceDate())
            item['subtotal'] = currency(obj.getSubtotal())
            item['vatamount'] = currency(obj.getVATAmount())
            item['total'] = currency(obj.getTotal())
        return items