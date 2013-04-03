from bika.lims.browser.client import ClientBatchesView
from bika.health import bikaMessageFactory as _


class BatchesView(ClientBatchesView):

    def __init__(self, context, request):
        super(BatchesView, self).__init__(context, request)
        self.title = _("Cases")
        self.columns['BatchID']['title'] = _('Case ID')
