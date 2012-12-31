from bika.lims.browser.sample import SamplesView
from bika.health.permissions import *


class BatchesView(SamplesView):
    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)
        self.contentFilter['DoctorUID'] = self.context.UID()
