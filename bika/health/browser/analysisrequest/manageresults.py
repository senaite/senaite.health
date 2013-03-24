from bika.lims.browser.analysisrequest import AnalysisRequestManageResultsView as BaseView
from bika.health.browser.analyses.view import AnalysesView


class ManageResultsView(BaseView):

    def createAnalysesView(self, context, request, **kwargs):
        return AnalysesView(context, request, **kwargs)
