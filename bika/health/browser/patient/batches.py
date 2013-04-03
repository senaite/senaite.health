from Products.CMFCore.utils import getToolByName
from bika.lims.browser.batchfolder import BatchFolderContentsView
from bika.health import bikaMessageFactory as _


class BatchesView(BatchFolderContentsView):

    def __init__(self, context, request):
        super(BatchesView, self).__init__(context, request)
        self.view_url = self.context.absolute_url() + "/batches"
        self.title = _("Cases")
        self.columns['BatchID']['title'] = _('Case ID')

    def contentsMethod(self, contentFilter):
        bc = getToolByName(self.context, "bika_catalog")
        batches = []
        for batch in bc(portal_type='Batch',
                        getPatientID=self.context.id):
            batch = batch.getObject()
            batches.append(batch)
        return batches
