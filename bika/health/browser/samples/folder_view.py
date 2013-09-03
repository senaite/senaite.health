from bika.lims.browser.sample import SamplesView as BaseView
from bika.health import bikaMessageFactory as _
from Products.CMFCore.utils import getToolByName


class SamplesView(BaseView):
    """ Overrides bika.lims.browser.sample.SamplesView
        Shows additional columns with info about the Patient
    """

    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)

        # Add Patient fields
        self.columns['getPatientID'] = {'title': _('Patient ID'), 'toggle': True}
        self.columns['getClientPatientID'] = {'title': _("Client PID"), 'toggle': True}
        self.columns['getPatient'] = {'title': _('Patient'), 'toggle': True}
        for rs in self.review_states:
            i = rs['columns'].index('getClientSampleID') + 1
            rs['columns'].insert(i, 'getClientPatientID')
            rs['columns'].insert(i, 'getPatientID')
            rs['columns'].insert(i, 'getPatient')

    def folderitems(self, full_objects=False):
        items = super(SamplesView, self).folderitems(full_objects)
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
            for rs in self.review_states:
                del rs['columns'][rs['columns'].index('getClientPatientID')]
                del rs['columns'][rs['columns'].index('getPatientID')]
                del rs['columns'][rs['columns'].index('getPatient')]
        else:
            for x in range(len(items)):
                if 'obj' not in items[x]:
                    items[x]['getClientPatientID'] = ''
                    items[x]['getPatientID'] = ''
                    items[x]['getPatient'] = ''
                    continue
                patient = self.getPatient(items[x]['obj'])
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
                else:
                    items[x]['getClientPatientID'] = ''
                    items[x]['getPatientID'] = ''
                    items[x]['getPatient'] = ''
        return items

    def getPatient(self, sample):
        # Onse sample can have more than one AR associated, but if is
        # the case, we must only take into account the one that is not
        # invalidated/retracted
        wf = getToolByName(self.context, 'portal_workflow')
        rawars = sample.getAnalysisRequests()
        ars = [ar for ar in rawars \
               if (wf.getInfoFor(ar, 'review_state') != 'invalid')]
        if (len(ars) == 0 and len(rawars) > 0):
            # All ars are invalid. Retrieve the info from the last one
            ar = rawars[len(rawars) - 1]
        elif (len(ars) > 1):
            # There's more than one valid AR
            # That couldn't happen never. Anyway, retrieve the last one
            ar = ars[len(ars) - 1]
        elif (len(ars) == 1):
            # One ar matches
            ar = ars[0]
        return ar.Schema()['Patient'].get(ar) if ar else None
