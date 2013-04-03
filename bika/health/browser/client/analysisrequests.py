from bika.lims.browser.client import ClientAnalysisRequestsView
from bika.health import bikaMessageFactory as _


class AnalysisRequestsView(ClientAnalysisRequestsView):
    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.columns['BatchID']['title'] = _('Case ID')
