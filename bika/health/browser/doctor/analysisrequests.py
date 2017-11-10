from bika.health.browser.analysisrequests.view import AnalysisRequestsView as BaseView


class AnalysisRequestsView(BaseView):
    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.contentFilter['getDoctorUID'] = self.context.UID()
