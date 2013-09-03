from bika.lims.browser.client import ClientAnalysisRequestsView as BaseClientARView
from bika.health.browser.analysisrequests.view import AnalysisRequestsView as \
    HealthAnalysisRequestsView


class AnalysisRequestsView(BaseClientARView, HealthAnalysisRequestsView):

    def __call__(self):
        return super(AnalysisRequestsView, self).__call__()
