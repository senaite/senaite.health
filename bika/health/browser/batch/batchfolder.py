from bika.lims.browser.batchfolder import BatchFolderContentsView as BaseView
from bika.health import bikaMessageFactory as _


class BatchFolderContentsView(BaseView):

    def __init__(self, context, request):
        super(BatchFolderContentsView, self).__init__(context, request)
        self.title = _("Cases")
