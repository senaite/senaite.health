from Products.CMFCore.utils import getToolByName
from bika.health.browser.batch.batchfolder import BatchFolderContentsView
from bika.health import bikaMessageFactory as _


class BatchesView(BatchFolderContentsView):

    def __init__(self, context, request):
        super(BatchesView, self).__init__(context, request)
        self.view_url = self.context.absolute_url() + "/batches"

        # Hide patient columns
        self.columns['getPatientID']['toggle'] = False
        self.columns['getClientPatientID']['toggle'] = False
        self.columns['Patient']['toggle'] = False

    def __call__(self):
        self.context_actions[_('Add')] = \
                {'url': self.portal.absolute_url() \
                        + '/batches/createObject?type_name=Batch',
                 'icon': self.portal.absolute_url() \
                        + '/++resource++bika.lims.images/add.png'}
        return BatchFolderContentsView.__call__(self)

    def contentsMethod(self, contentFilter):
        bc = getToolByName(self.context, "bika_catalog")
        batches = []
        proxies = bc(portal_type='Batch',
                     getPatientID=self.context.getPatientID())
        for batch in proxies:
            batch = batch.getObject()
            batches.append(batch)
        return batches
