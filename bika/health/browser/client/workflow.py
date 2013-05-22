from bika.lims.browser.client import ClientWorkflowAction as BaseClass
from bika.health.browser.analysisrequest.publish import AnalysisRequestPublish


class ClientWorkflowAction(BaseClass):

    def doPublish(self, context, request, action, analysis_requests):
        return AnalysisRequestPublish(context, request, action, analysis_requests)
