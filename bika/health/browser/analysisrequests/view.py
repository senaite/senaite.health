from bika.lims.browser.analysisrequest import AnalysisRequestsView as BaseView
from bika.health import bikaMessageFactory as _
from Products.CMFCore.utils import getToolByName


class AnalysisRequestsView(BaseView):
    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.columns['BatchID']['title'] = _('Case ID')

        # Add Client Patient fields
        self.columns['getPatientID'] = {'title': _('Patient ID'), 'toggle': True}
        self.columns['getClientPatientID'] = {'title': _("Client PID"), 'toggle': True}
        self.columns['getPatient'] = {'title': _('Patient'), 'toggle': True}
        self.columns['getProvince'] = {'title': _('Province'), 'toggle': True}
        self.columns['getDistrict'] = {'title': _('District'), 'toggle': True}
        for rs in self.review_states:
            i = rs['columns'].index('BatchID') + 1
            rs['columns'].insert(i, 'getClientPatientID')
            rs['columns'].insert(i, 'getPatientID')
            rs['columns'].insert(i, 'getDistrict')
            rs['columns'].insert(i, 'getProvince')
            rs['columns'].insert(i, 'getPatient')

    def folderitems(self, full_objects=False):
        items = super(AnalysisRequestsView, self).folderitems(full_objects)
        items = self.filteritems(items)
        pm = getToolByName(self.context, "portal_membership")
        member = pm.getAuthenticatedMember()
        roles = member.getRoles()
        if 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles:
            # Remove patient fields. Must be done here because in __init__ 
            # method, member.getRoles() returns empty
            del self.columns['getPatientID']
            del self.columns['getClientPatientID']
            del self.columns['getPatient']
            del self.columns['getProvince']
            del self.columns['getDistrict']
            for rs in self.review_states:
                del rs['columns'][rs['columns'].index('getClientPatientID')]
                del rs['columns'][rs['columns'].index('getPatientID')]
                del rs['columns'][rs['columns'].index('getPatient')]
                del rs['columns'][rs['columns'].index('getProvince')]
                del rs['columns'][rs['columns'].index('getDistrict')]
        else:
            for x in range(len(items)):
                if 'obj' not in items[x]:
                    items[x]['getClientPatientID'] = ''
                    items[x]['getPatientID'] = ''
                    items[x]['getPatient'] = ''
                    items[x]['getProvince'] = ''
                    items[x]['getDistrict'] = ''
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
                    items[x]['getPatient'] = patient.Title()
                    items[x]['replace']['getPatient'] = "<a href='%s'>%s</a>" % \
                        (patient.absolute_url(), items[x]['getPatient'])
                    items[x]['getProvince'] = patient.getProvince()
                    items[x]['getDistrict'] = patient.getDistrict()
                else:
                    items[x]['getClientPatientID'] = ''
                    items[x]['getPatientID'] = ''
                    items[x]['getPatient'] = ''
                    items[x]['getProvince'] = ''
                    items[x]['getDistrict'] = ''
        return items

    def filteritems(self, items):
        return items
