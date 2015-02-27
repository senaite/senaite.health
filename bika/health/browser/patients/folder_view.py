from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import logged_in_client
from bika.health.config import PROJECTNAME
from bika.health.interfaces import IPatients
from bika.health.permissions import *
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
import json


class PatientsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(PatientsView, self).__init__(context, request)

        self.catalog = 'bika_patient_catalog'

        self.contentFilter = {'portal_type': 'Patient',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.title = self.context.translate(_("Patients"))
        self.icon = self.portal_url + "/++resource++bika.health.images/patient_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25

        self.columns = {

            'Title': {'title': _('Patient'),
                      'index': 'sortable_title'},

            'getPatientID': {'title': _('Patient ID'),
                             'index': 'getPatientID'},

            'getClientPatientID': {'title': _('Client PID'),
                            'index': 'getClientPatientID'},

            'getGender': {'title': _('Gender'),
                          'index': 'getGender',
                          'toggle': True},

            'getAgeSplittedStr': {'title': _('Age'),
                                  'index': 'getAgeSplittedStr',
                                  'toggle': True},

            'getBirthDate': {'title': _('BirthDate'),
                             'index': 'getBirthDate',
                             'toggle': True},

            'getCitizenship': {'title': _('Citizenship'),
                               'index': 'getCitizenship',
                               'toggle': True},

            'getPrimaryReferrer': {'title': _('Primary Referrer'),
                                   'index': 'getPrimaryReferrerTitle',
                                   'toggle': True},

        }

        self.review_states = [
            {'id': 'default',
             'title': _b('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [],
             'columns': ['getPatientID', 'getClientPatientID',
                         'Title', 'getGender', 'getAgeSplittedStr',
                         'getBirthDate', 'getCitizenship', 'getPrimaryReferrer']},
        ]

    def __call__(self):
        self._initFormParams()
        return super(PatientsView, self).__call__()

    def _initFormParams(self):
        mtool = getToolByName(self.context, 'portal_membership')
        addPortalMessage = self.context.plone_utils.addPortalMessage
        if mtool.checkPermission(AddPatient, self.context):
            clients = self.context.clients.objectIds()
            if clients:
                self.context_actions[_b('Add')] = {
                    'url': 'createObject?type_name=Patient',
                    'icon': '++resource++bika.lims.images/add.png'
                }
            else:
                msg = _("Cannot create patients without any system clients configured.")
                addPortalMessage(self.context.translate(msg))
        if mtool.checkPermission(ViewPatients, self.context):
            self.review_states[0]['transitions'].append({'id':'deactivate'})
            self.review_states.append(
                {'id': 'inactive',
                 'title': _b('Dormant'),
                 'contentFilter': {'inactive_state': 'inactive'},
                 'transitions': [{'id':'activate'}, ],
                 'columns': ['getPatientID', 'getClientPatientID',
                             'Title', 'getGender', 'getAgeSplittedStr',
                             'getBirthDate', 'getCitizenship', 'getPrimaryReferrer']})
            self.review_states.append(
                {'id': 'all',
                 'title': _b('All'),
                 'contentFilter':{},
                 'transitions':[{'id':'empty'}, ],
                 'columns': ['Title', 'getPatientID', 'getClientPatientID',
                             'getGender', 'getAgeSplittedStr',
                             'getBirthDate', 'getCitizenship',
                             'getPrimaryReferrer']})
            stat = self.request.get("%s_review_state" % self.form_id, 'default')
            self.show_select_column = stat != 'all'


    def folderitems(self):
        # Obtain the member and member's role.
        pm = getToolByName(self.context, "portal_membership")
        member = pm.getAuthenticatedMember()
        roles = member.getRoles()
        # Limit results to those patients that "belong" to the member's client
        if 'Client' in roles:
            # It obtains the referrer institution which the current AuthenticatedMember belong.
            client = logged_in_client(self.context, member)
            self.contentFilter['getPrimaryReferrerUID'] = client.UID()
            # hide PrimaryReferrer column
            new_states = []
            for x in self.review_states:
                if 'getPrimaryReferrer' in x['columns']:
                    x['columns'].remove("getPrimaryReferrer")
                new_states.append(x)
            self.review_states = new_states

        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']
            items[x]['getPatientID'] = obj.getPatientID()
            items[x]['getBirthDate'] = self.ulocalized_time(obj.getBirthDate())
            items[x]['replace']['getPatientID'] = "<a href='%s/analysisrequests'>%s</a>" % \
                (items[x]['url'], items[x]['getPatientID'])
            items[x]['replace']['getClientPatientID'] = "<a href='%s'>%s</a>" % \
                (items[x]['url'], items[x]['getClientPatientID'])
            items[x]['replace']['Title'] = "<a href='%s/analysisrequests'>%s</a>" % \
                (items[x]['url'], items[x]['Title'])
            if 'Client' not in roles:
                # All the patients don't belong to the same client.
                pr = obj.getPrimaryReferrer()
                if pr:
                    items[x]['getPrimaryReferrer'] = pr.Title()
                    items[x]['replace']['getPrimaryReferrer'] = "<a href='%s/analysisrequests'>%s</a>" % \
                    (pr.absolute_url(), pr.Title())
                else:
                    items[x]['getPrimaryReferrer'] = ''

        return items
