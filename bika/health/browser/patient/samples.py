from bika.lims.browser.sample import SamplesView
from bika.health.permissions import *


class SamplesView(SamplesView):
    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)
        self.contentFilter['getPatientUID'] = self.context.UID()
