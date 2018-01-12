# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.interface.declarations import implements
from plone.app.content.browser.interfaces import IFolderContentsView
from bika.lims.permissions import AddInvoice
from bika.lims.permissions import ManageInvoices
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.invoicefolder import InvoiceFolderContentsView
from bika.lims.utils import currency_format


from bika.lims.permissions import AddInvoice
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _

""" This file contains an invoice type folder to be used in insurance company's stuff.
"""

class InvoiceFolderView(BikaListingView):
    """
    This class will build a list with the invoices that comes from the current Insurance Company's
    patient.
    """
    implements(IFolderContentsView)

    def __init__(self, context, request):
        super(InvoiceFolderView, self).__init__(context, request)
        self.catalog = 'portal_catalog'
        self.contentFilter = {'portal_type': 'Invoice',
                              'sort_on': 'sortable_title',
                              'sort_order': 'reverse'}
        self.context_actions = {}
        self.title = self.context.translate(_("Invoices"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/invoice_big.png"
        self.description = "The invoices of Insurance Company's patients"
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
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

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(ManageInvoices, self.context):
            self.show_select_column = True
        return super(InvoiceFolderView, self).__call__()

    def isItemAllowed(self, obj):
        """
        Check if the invoice should be shown in the insurance company's invoice folder.
        To be shown the invoice should be related with a insurance company's patient.
        :obj: An invoice object.
        :return: True/False
        """
        iAR = obj.getAnalysisRequest() if obj.getAnalysisRequest() else None
        # Get the AR's patient if the invoice has an AR related
        patient = iAR.Schema()['Patient'].get(iAR) if iAR else None
        # Get the patient's insurance company's UID if there is a patient
        icuid = patient.getInsuranceCompany().UID() \
                if patient and patient.getInsuranceCompany() else None
        return icuid == self.context.UID()

    def folderitems(self, full_objects=False):
        """
        :return: All the invoices related with the Insurance Company's clients.
        """
        currency = currency_format(self.context, 'en')
        self.show_all = True
        items = BikaListingView.folderitems(self, full_objects)
        l = []
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
            l.append(item)
        return l
