from bika.health.browser.analysisrequests.view import AnalysisRequestsView as BaseView


class AnalysisRequestsView(BaseView):
    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.contentFilter['DoctorUID'] = self.context.UID()

    def isItemAllowed(self, obj):
        """
        Checks the BikaLIMS conditions and also checks filter bar conditions
        @Obj: it is an analysis request brain.
        @return: boolean
        """
        if not super(AnalysisRequestsView, self).isItemAllowed(obj):
            return False
        return self.context.UID() == obj.getDoctorUID
