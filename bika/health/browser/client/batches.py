# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.lims.browser.client import ClientBatchesView as BaseClientBatchesView
from bika.health.browser.batch.batchfolder import BatchFolderContentsView as HealthBatchesView


class BatchesView(BaseClientBatchesView, HealthBatchesView):

    def __call__(self):
        url = self.portal.absolute_url()
        self.context_actions[_('Add')] = dict(
            url="{}{}".format(url, "/batches/createObject?type_name=Batch"),
            icon="{}{}".format(url, "/++resource++bika.lims.images/add.png"))

        return HealthBatchesView.__call__(self)
