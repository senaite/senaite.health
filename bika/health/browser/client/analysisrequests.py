from bika.lims.browser.client import ClientAnalysisRequestsView
from bika.health import bikaMessageFactory as _
from Products.CMFCore.utils import getToolByName


class AnalysisRequestsView(ClientAnalysisRequestsView):
    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.columns['BatchID']['title'] = _('Case ID')

    def folderitems(self, full_objects=False):
        items = super(AnalysisRequestsView, self).folderitems(full_objects)
        pm = getToolByName(self.context, "portal_membership")
        member = pm.getAuthenticatedMember()
        roles = member.getRoles()
        if 'Manager' in roles or 'LabManager' in roles or 'LabClerk' in roles:
            # Add Client Patient fields
            self.columns['getPatientID'] = {'title': _('Patient ID')}
            self.columns['getClientPatientID'] = {'title': _("Client PID")}
            for rs in self.review_states:
                i = rs['columns'].index('BatchID') + 1
                rs['columns'].insert(i, 'getClientPatientID')
                rs['columns'].insert(i, 'getPatientID')

            for x in range(len(items)):
                if 'obj' not in items[x]:
                    items[x]['getClientPatientID'] = ''
                    items[x]['getPatientID'] = ''
                    continue
                obj = items[x]['obj']
                patient = obj.Schema()['Patient'].get(obj)
                if patient:
                    items[x]['getPatientID'] = patient.getPatientID()
                    items[x]['replace']['getPatientID'] = "<a href='%s'>%s</a>" % \
                        (patient.absolute_url(), items[x]['getPatientID'])
                    items[x]['getClientPatientID'] = patient.getClientPatientID()
                    items[x]['replace']['getClientPatientID'] = "<a href='%s'>%s</a>" % \
                        (patient.absolute_url(), items[x]['getClientPatientID'])
                else:
                    items[x]['getClientPatientID'] = ''
                    items[x]['getPatientID'] = ''
        return items