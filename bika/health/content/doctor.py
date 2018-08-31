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
        return [p.getObject() for p in bc(portal_type='AnalysisRequest', getDoctorUID=self.UID())]

    def get_clients(self):
        """
        Vocabulary list with clients which the user has Manage AR rights.
        :return: A DisplayList object
        """
        query = dict(portal_type='Client', inactive_state='active', sort_order='ascending',
                     sort_on='title')
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
