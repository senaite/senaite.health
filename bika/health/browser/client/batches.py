# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.lims.browser.client import ClientBatchesView as BaseClientBatchesView
from bika.health.browser.batch.batchfolder import BatchFolderContentsView as HealthBatchesView


class BatchesView(BaseClientBatchesView, HealthBatchesView):

    def contentsMethod(self, contentFilter):
        batches = {}
        bc = getToolByName(self.context, "bika_catalog")
        for batch in bc(portal_type='Batch',
                        getClientUID = self.context.UID()):
            batch = batch.getObject()
            batches[batch.UID()] = batch 
        return batches.values()
