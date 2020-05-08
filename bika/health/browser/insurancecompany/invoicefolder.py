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

from plone.app.content.browser.interfaces import IFolderContentsView
from Products.CMFCore.utils import getToolByName
from zope.interface.declarations import implements

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import ManageInvoices
from bika.lims.utils import currency_format
from bika.lims.utils import get_link

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

    def before_render(self):
        """Before template render hook
        """
        super(InvoiceFolderView, self).before_render()
        # Don't allow any context actions on Invoices folder
        self.request.set("disable_border", 1)

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

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        currency = currency_format(self.context, 'en')
        item['replace']['id'] = get_link(item["url"], api.get_id(obj))
        item['client'] = obj.getClient().Title()
        item['invoicedate'] = self.ulocalized_time(obj.getInvoiceDate())
        item['subtotal'] = currency(obj.getSubtotal())
        item['vatamount'] = currency(obj.getVATAmount())
        item['total'] = currency(obj.getTotal())
        return item
