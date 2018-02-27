# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import types

from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.health.catalog import CATALOG_PATIENT_LISTING
from bika.health.permissions import *
from bika.lims import bikaMessageFactory as _b, api
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IClient, ILabContact
from bika.lims.utils import get_link
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

# Available Columns of the Patients View Table (see: `get_columns`)
COLUMNS = ['getPatientID',
           'getClientPatientID',
           'Title',
           'getGender',
           'getAgeSplittedStr',
           'getBirthDate',
           'getPrimaryReferrerTitle']


class PatientsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(PatientsView, self).__init__(context, request)

        self.catalog = CATALOG_PATIENT_LISTING

        self.contentFilter = {'portal_type': 'Patient',
                              'sort_on': 'getPatientID',
                              'sort_order': 'reverse'}
        self.context_actions = {}
        self.title = self.context.translate(_("Patients"))
        self.icon = '{}/++resource++bika.health.images/patient_big.png'.format(
            self.portal_url)
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False

        self.columns = {
            'Title': {
                'title': _('Patient'),
                'index': 'Title',
                'replace_url': 'getURL'},

            'getPatientID': {
                'title': _('Patient ID'),
                'index': 'getPatientID',
                'replace_url': 'getURL'},

            'getClientPatientID': {
                'title': _('Client PID'),
                'replace_url': 'getURL',
                'sortable': False},

            'getGender': {
                'title': _('Gender'),
                'toggle': True,
                'sortable': False},

            'getAgeSplittedStr': {
                'title': _('Age'),
                'toggle': True,
                'sortable': False},

            'getBirthDate': {
                'title': _('BirthDate'),
                'toggle': True,
                'sortable': False},

            'getPrimaryReferrerTitle': {
                'title': _('Primary Referrer'),
                'replace_url': 'getPrimaryReferrerURL',
                'toggle': True,
                'sortable': False},
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
        # Filter by client if necessary
        self._apply_filter_by_client()
        return super(PatientsView, self).__call__()

    def _apply_filter_by_client(self):
        # If the current context is a Client, filter Patients by Client UID
        if IClient.providedBy(self.context):
            client_uid = api.get_uid(self.context)
            self.contentFilter['getPrimaryReferrerUID'] = client_uid
            return

        # If the current user is a Client contact, filter the Patients in
        # accordance. For the rest of users (LabContacts), the visibility of
        # the patients depend on their permissions
        user = api.get_current_user()
        roles = user.getRoles()
        if 'Client' not in roles:
            return

        # Are we sure this a ClientContact?
        # May happen that this is a Plone member, w/o having a ClientContact
        # assigned or having a LabContact assigned... weird
        contact = api.get_user_contact(user)
        if not contact or ILabContact.providedBy(contact):
            return

        # Is the parent from the Contact a Client?
        client = api.get_parent(contact)
        if not client or not IClient.providedBy(client):
            return
        client_uid = api.get_uid(client)
        self.contentFilter['getPrimaryReferrerUID'] = client_uid

    def get_columns(self, sieve=None):
        """Get Table Columns and filter out keys listed in sieve
        """
        if sieve is None:
            sieve = list()
        if type(sieve) not in (types.ListType, types.TupleType):
            raise RuntimeError("Sieve must be a list type")
        # filter out columns listed in sieve
        return filter(lambda c: c not in sieve, COLUMNS)

    def _initFormParams(self):
        mtool = getToolByName(self.context, 'portal_membership')
        addPortalMessage = self.context.plone_utils.addPortalMessage
        can_add_patients = mtool.checkPermission(AddPatient, self.context)

        if not can_add_patients and IClient.providedBy(self.context):
            # The user logged in is a Contact from this Client?
            # Tip: when a client contact is created, bika.lims assigns that
            # contact as the owner of the client, so he/she can access to the
            # Client he/she is owner of but not to the rest of Clients.
            # See bika.lims.browser.contact._link_user(userid)
            client = self.context
            owners = client.users_with_local_role('Owner')
            member = mtool.getAuthenticatedMember()
            can_add_patients = member.id in owners

        if can_add_patients:
            # TODO Performance tweak. Is this really needed?
            clients = self.context.clients.objectIds()
            if clients:
                add_patient_url = '{}/patients/createObject?type_name=Patient'\
                                  .format(self.portal_url)
                self.context_actions[_b('Add')] = {
                    'url': add_patient_url,
                    'icon': '++resource++bika.lims.images/add.png'
                }
            else:
                msg = _("Cannot create patients without any system clients "
                        "configured.")
                addPortalMessage(self.context.translate(msg))

        if mtool.checkPermission(ViewPatients, self.context):
            self.review_states[0]['transitions'].append({'id': 'deactivate'})
            self.review_states.append(
                {'id': 'inactive',
                 'title': _b('Dormant'),
                 'contentFilter': {'inactive_state': 'inactive'},
                 'transitions': [{'id': 'activate'}, ],
                 'columns': self.get_columns()})
            self.review_states.append(
                {'id': 'all',
                 'title': _b('All'),
                 'contentFilter': {},
                 'transitions': [{'id': 'empty'}, ],
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
        item['getBirthDate'] = self.ulocalized_time(obj.getBirthDate)
        # make the columns patient title, patient ID and client patient ID
        # redirect to the Analysis Requests of the patient
        columns_to_redirect = ['Title', 'getPatientID', 'getClientPatientID']
        for column in columns_to_redirect:
            item = self._redirect_column_to_patients_ar(column, item, obj)
        return item

    def folderitems(self):
        return BikaListingView.folderitems(self, classic=False)

    def _redirect_column_to_patients_ar(self, column_name, item, obj):
        """ Given the name of a column shown in the view make the column
        value for each patient redirect to the Analysis Requests of the
        patient.

        :param column_name: Name of the column that has to redirect to ARs
        :param obj: obj from where to extract the column data. The instance of
        the class to be foldered
        :param item: dictionary containing the properties of the object to be used by
        the template
        :return: dictionary containing the properties of the object to be used by
        the template updated with the redirect info
        """
        # We want to avoid showing the link on columns that have no value and this
        # is why we check if the attribute exists and has a value
        if hasattr(obj, column_name) and getattr(obj, column_name):
            patient_ar_url = "/".join([obj.getURL(), 'analysisrequests'])
            item['replace'][column_name] = get_link(patient_ar_url, getattr(obj, column_name))
        return item
