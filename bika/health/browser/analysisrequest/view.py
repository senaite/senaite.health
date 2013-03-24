from bika.lims.browser.analysisrequest import AnalysisRequestViewView
from bika.health.browser.analyses.view import AnalysesView


class AnalysisRequestView(AnalysisRequestViewView):

    def createAnalysesView(self, context, request, **kwargs):
        return AnalysesView(context, request, **kwargs)
