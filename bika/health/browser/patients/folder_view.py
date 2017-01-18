# -*- coding: utf-8 -*-
import types

from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.health.catalog import CATALOG_PATIENT_LISTING
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

# Available Columns of the Patients View Table (see: `get_columns`)
COLUMNS = ['getPatientID',
           'getClientPatientID',
           'Title',
           'getGender',
           'getAgeSplittedStr',
           'getBirthDate',
           'getPrimaryReferrer']


class PatientsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(PatientsView, self).__init__(context, request)

        self.catalog = CATALOG_PATIENT_LISTING

        self.contentFilter = {'portal_type': 'Patient',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.title = self.context.translate(_("Patients"))
        self.icon = self.portal_url + "/++resource++bika.health.images/patient_big.png"
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False

        self.columns = {

            'Title': {'title': _('Patient'),
                      'index': 'sortable_title'},

            'getPatientID': {'title': _('Patient ID'), },

            'getClientPatientID': {'title': _('Client PID'), },

            'getGender': {'title': _('Gender'),
                          'toggle': True},

            'getAgeSplittedStr': {'title': _('Age'),
                                  'toggle': True},

            'getBirthDate': {'title': _('BirthDate'),
                             'toggle': True},

            'getPrimaryReferrer': {'title': _('Primary Referrer'),
                                   'toggle': True},

        }

        self.review_states = [
            {'id': 'default',
             'title': _b('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [],
             'columns': self.get_columns()},
        ]

    def __call__(self):
        self._initFormParams()
        return super(PatientsView, self).__call__()

    def get_columns(self, sieve=[]):
        """Get Table Columns and filter out keys listed in sieve
        """
        if type(sieve) not in (types.ListType, types.TupleType):
            raise RuntimeError("Sieve must be a list type")
        # filter out columns listed in sieve
        return filter(lambda c: c not in sieve, COLUMNS)

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
                 'columns': self.get_columns()})
            self.review_states.append(
                {'id': 'all',
                 'title': _b('All'),
                 'contentFilter':{},
                 'transitions':[{'id':'empty'}, ],
                 'columns': self.get_columns()})
            stat = self.request.get("%s_review_state" % self.form_id, 'default')
            self.show_select_column = stat != 'all'

    def folderitem(self, obj, item, index):
        """ Service triggered each time an item is iterated in folderitems.
            The use of this service prevents the extra-loops in child objects.
            :obj: the instance of the class to be foldered
            :item: dict containing the properties of the object to be used by
                the template
            :index: current index of the item
        """
        if 'obj' not in item:
            return None
        # TODO: Remember to use https://github.com/bikalabs/bika.lims/pull/1846/files#diff-40dfcc4bde98b3ea8f3d9f985776675aR51
        # Note: attr and replace_url
        item['getPatientID'] = obj.getPatientID
        item['getGender'] = obj.getGender
        item['getAgeSplittedStr'] = obj.getAgeSplittedStr
        item['getBirthDate'] = self.ulocalized_time(obj.getBirthDate)
        item['getClientPatientID'] = obj.getClientPatientID
        item['Title'] = obj.Title
        item['replace']['getPatientID'] = "<a href='%s/analysisrequests'>%s</a>" % \
            (item['url'], item['getPatientID'])
        item['replace']['getClientPatientID'] = "<a href='%s'>%s</a>" % \
            (item['url'], item['getClientPatientID'])
        item['replace']['Title'] = "<a href='%s/analysisrequests'>%s</a>" % \
            (item['url'], item['Title'])
        # Obtain the member and member's role.
        pm = getToolByName(self.context, "portal_membership")
        member = pm.getAuthenticatedMember()
        roles = member.getRoles()
        if 'Client' not in roles:
            # All the patients don't belong to the same client.
            prTitle = obj.getPrimaryReferrerTitle
            prURL = obj.getPrimaryReferrerURL
            item['getPrimaryReferrerTitle'] = prTitle
            item['replace']['getPrimaryReferrer'] = \
                "<a href='%s/analysisrequests'>%s</a>" % \
                (prURL, prTitle)
        return item

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
        items = BikaListingView.folderitems(self, classic=False)
        return items
