from bika.health.browser.patients.folder_view import PatientsView
from Products.CMFCore.utils import getToolByName
from bika.health.permissions import AddPatient
from bika.lims import bikaMessageFactory as _b


class ClientPatientsView(PatientsView):

    def __init__(self, context, request):
        super(ClientPatientsView, self).__init__(context, request)
        # Limit results to those patients that "belong" to this client
        self.contentFilter['getPrimaryReferrerUID'] = context.UID()

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        # New Patient: Use this space to equip the add form with client UID
        if mtool.checkPermission(AddPatient, self.context):
            clients = self.context.clients.objectIds()
            if clients:
                self.context_actions[_b('Add')] = {
                    'url': 'createObject?type_name=Patient',
                    'icon': '++resource++bika.lims.images/add.png'
                }

    def folderitems(self):
        folderitems = super(ClientPatientsView, self).folderitems()

        # hide PrimaryReferrer column
        new_states = []
        for x in self.review_states:
            if 'getPrimaryReferrer' in x['columns']:
                x['columns'].remove("getPrimaryReferrer")
            new_states.append(x)
        self.review_states = new_states

        return folderitems
