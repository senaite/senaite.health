from bika.lims.browser.analysisrequest import AnalysisRequestsView


class AnalysisRequestsView(AnalysisRequestsView):
    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.contentFilter['DoctorUID'] = self.context.UID()
