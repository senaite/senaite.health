# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH.
#
# SENAITE.HEALTH is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.Archetypes import atapi
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from bika.health import bikaMessageFactory as _
from bika.health.config import *
from bika.health.interfaces import IDoctor
from bika.lims import api
from bika.lims import idserver
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.content.contact import Contact
from zope.interface import implements

schema = Contact.schema.copy() + Schema((
    StringField('DoctorID',
        required=1,
        searchable=True,
        widget=StringWidget(
            label=_('Doctor ID'),
        ),
    ),
    ReferenceField(
        'PrimaryReferrer',
        vocabulary='get_clients_vocabulary',
        allowed_types=('Client',),
        relationship='DoctorClient',
        required=0,
        widget=SelectionWidget(
            format='select',
            description=_('Associate the doctor to a client. '
                          'This doctor will not be accessible from '
                          'other clients.'),
            label=_('Client'),
        ),
    ),
))


class Doctor(Contact):
    implements(IDoctor)
    _at_rename_after_creation = True
    displayContentsTab = False
    schema = schema

    def _renameAfterCreation(self, check_auto_id=False):
        """Autogenerate the ID of the object based on core's ID formatting
        settings for this type
        """
        idserver.renameAfterCreation(self)

    def getSamples(self, full_objects=False):
        """
        Returns the Samples this Doctor is assigned to
        :return:
        """
        query = dict(portal_type="Sample", getDoctorUID=self.UID())
        brains = api.search(query, "bika_catalog")
        if full_objects:
            return map(lambda brain: api.get_object(brain), brains)
        return brains

    def getAnalysisRequests(self, full_objects=False):
        """
        Returns the Analysis Requests this Doctor is assigned to
        :return:
        """
        query = dict(portal_type='AnalysisRequest', getDoctorUID=self.UID())
        brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
        if full_objects:
            return map(lambda brain: api.get_object(brain), brains)
        return brains

    def getBatches(self, full_objects=False):
        """
        Returns the Batches this Doctor is assigned to
        :return:
        """
        query = dict(portal_type='Batch', getDoctorUID=self.UID())
        brains = api.search(query, 'bika_catalog')
        if full_objects:
            return map(lambda brain: api.get_object(brain), brains)
        return brains

    def get_clients_vocabulary(self):
        """
        Vocabulary list with clients
        :return: A DisplayList object
        """
        if self.getBatches() or self.getAnalysisRequests():
            # Allow to change the client if there are no ARs associated
            client = self.getPrimaryReferrer()
            if not client:
                # Maybe all Batches and ARs assigned to this Doctor belong to
                # the same Client.. If so, just assign this client by default
                client_uids = map(lambda ar: ar.getClientUID,
                                  self.getAnalysisRequests())
                client_uids = list(set(client_uids))
                if len(client_uids) > 1:
                    # More than one client assigned!
                    return DisplayList([('', '')])
                clients = map(lambda batch: batch.getClient(),
                              self.getBatches(full_objects=True))
                client_uids += map(lambda client: api.get_uid(client), clients)
                client_uids = list(set(client_uids))
                if len(client_uids) > 1:
                    # More than one client assigned!
                    return DisplayList([('', '')])

                client = api.get_object_by_uid(client_uids[0])

            return DisplayList([(api.get_uid(client), client.Title())])

        # If the current user is a client contact, do not display other clients
        client = api.get_current_client()
        if client:
            return DisplayList([(api.get_uid(client), client.Title())])

        # Search for clients
        query = dict(portal_type='Client', is_active=True,
                     sort_order='ascending', sort_on='title')
        brains = api.search(query, 'portal_catalog')
        clients = map(lambda brain: [api.get_uid(brain), brain.Title], brains)
        clients.insert(0, ['', ''])
        return DisplayList(clients)

    def getPrimaryReferrerUID(self):
        primary_referrer = self.getPrimaryReferrer()
        if primary_referrer:
            return primary_referrer.UID()

    def current_user_can_edit(self):
        """Returns true if the current user can edit this Doctor.
        """
        user_client = api.get_current_client()
        if user_client:
            # The current user is a client contact. This user can only edit
            # this doctor if it has the same client assigned
            client_uid = api.get_uid(user_client)
            doctor_client = self.getPrimaryReferrer()
            return doctor_client and api.get_uid(doctor_client) == client_uid
        return True

atapi.registerType(Doctor, PROJECTNAME)
