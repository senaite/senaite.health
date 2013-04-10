from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
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
        self.title = _("Patients")
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
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions':[{'id':'empty'}, ],
             'columns': ['Title', 'getPatientID', 'getGender', 'getAgeSplittedStr',
                         'getBirthDate', 'getCitizenship', 'getPrimaryReferrer']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        addPortalMessage = self.context.plone_utils.addPortalMessage
        if mtool.checkPermission(AddPatient, self.context):
            clients = self.context.clients.objectIds()
            if clients:
                self.context_actions[_('Add')] = {
                    'url': 'createObject?type_name=Patient',
                    'icon': '++resource++bika.lims.images/add.png'
                }
            else:
                msg = _("Cannot create patients without any system clients configured.")
                addPortalMessage(self.context.translate(msg))
        return super(PatientsView, self).__call__()

    def folderitems(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(ManagePatients, self.context):
            del self.review_states[0]['transitions']
            self.show_select_column = True
            self.review_states.append(
                {'id': 'active',
                 'title': _('Active'),
                 'contentFilter': {'inactive_state': 'active'},
                 'transitions': [{'id':'deactivate'}, ],
                 'columns': ['getPatientID', 'Title', 'getGender', 'getAgeSplittedStr',
                             'getBirthDate', 'getCitizenship', 'getPrimaryReferrer']})
            self.review_states.append(
                {'id': 'inactive',
                 'title': _('Dormant'),
                 'contentFilter': {'inactive_state': 'inactive'},
                 'transitions': [{'id':'activate'}, ],
                 'columns': ['getPatientID', 'Title', 'getGender', 'getAgeSplittedStr',
                             'getBirthDate', 'getCitizenship', 'getPrimaryReferrer']})

        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']
            items[x]['getPatientID'] = obj.getPatientID()
            items[x]['getBirthDate'] = self.ulocalized_time(obj.getBirthDate())
            items[x]['replace']['getPatientID'] = "<a href='%s/analysisrequests'>%s</a>" % \
                (items[x]['url'], items[x]['getPatientID'])
            items[x]['replace']['Title'] = "<a href='%s/analysisrequests'>%s</a>" % \
                (items[x]['url'], items[x]['Title'])

            pr = obj.getPrimaryReferrer()
            if pr:
                items[x]['getPrimaryReferrer'] = pr.Title()
                items[x]['replace']['getPrimaryReferrer'] = "<a href='%s/analysisrequests'>%s</a>" % \
                    (pr.absolute_url(), pr.Title())
            else:
                items[x]['getPrimaryReferrer'] = ''

        return items
