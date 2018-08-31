# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

"""
"""
from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.CMFCore.utils import getToolByName
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from zope.interface import implements

from bika.lims import api

from bika.health import bikaMessageFactory as _
from bika.health.config import *
from bika.health.interfaces import IDoctor
from bika.lims.content.contact import Contact

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
        vocabulary='get_clients',
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
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    security.declarePublic('getSamples')

    def getSamples(self):
        bc = getToolByName(self, 'bika_catalog')
        return [p.getObject() for p in bc(portal_type='Sample', getDoctorUID=self.UID())]

    security.declarePublic('getARs')

    def getARs(self, analysis_state):
        bc = getToolByName(self, 'bika_catalog')
        return [p.getObject() for p in bc(portal_type='AnalysisRequest',
                                          getDoctorUID=self.UID())]

    def getAnalysisRequests(self):
        """
        Returns the Analysis Requests this Doctor is assigned to
        :return:
        """
        query = dict(portal_type='AnalysisRequest', getDoctorUID=self.UID())
        return api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)

    def getBatches(self):
        """
        Returns the Batches this Doctor is assigned to
        :return:
        """
        query = dict(portal_type='Batch', getDoctorUID=self.UID())
        return api.search(query, 'bika_catalog')

    def get_clients(self):
        """
        Vocabulary list with clients
        :return: A DisplayList object
        """
        if self.getBatches() or self.getAnalysisRequests():
            # Allow to change the client if there are no ARs associated
            client = self.getPrimaryReferrer()
            if not client:
                return DisplayList([('', '')])
            return DisplayList([(api.get_uid(client), client.Title())])

        # If the current user is a client contact, do not display other clients
        client = api.get_current_client()
        if client:
            return DisplayList([(api.get_uid(client), client.Title())])

        # Search for clients
        query = dict(portal_type='Client', inactive_state='active',
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
