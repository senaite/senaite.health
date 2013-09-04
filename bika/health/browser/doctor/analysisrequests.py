from bika.health.browser.analysisrequests.view import AnalysisRequestsView as BaseView


class AnalysisRequestsView(BaseView):
    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.contentFilter['DoctorUID'] = self.context.UID()

    def filteritems(self, items):
        outitems = []
        for x in range(len(items)):
            if 'obj' in items[x]:
                ar = items[x]['obj']
                doctor = ar.Schema()['Doctor'].get(ar) if 'Doctor' in ar.Schema() else None
                if (doctor and doctor.UID() == self.context.UID()):
                    outitems.append(items[x])
        return outitems
