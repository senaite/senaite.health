from Products.CMFCore.utils import getToolByName
from bika.lims.browser.batchfolder import BatchFolderContentsView
from bika.health.permissions import *


class BatchesView(BatchFolderContentsView):

    def __init__(self, context, request):
        super(BatchesView, self).__init__(context, request)
        self.view_url = self.context.absolute_url() + "/batches"

    def contentsMethod(self, contentFilter):
        bc = getToolByName(self.context, "bika_catalog")
        state = [x for x in self.review_states if x['id'] == self.review_state][0]
        batches = []
        for batch in bc(portal_type='Batch',
                        getPatientUID=self.context.UID()):
            batch = batch.getObject()
            batches.append(batch)
        return batches
