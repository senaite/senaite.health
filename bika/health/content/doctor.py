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
        # Only show clients to which we have Manage AR rights.
        mtool = api.get_tool('portal_membership')
        clientfolder = self.clients
        clients = []
        for client in clientfolder.objectValues("Client"):
            if not mtool.checkPermission(ManageAnalysisRequests, client):
                continue
            clients.append([client.UID(), client.Title()])
        clients.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        clients.insert(0, ['', ''])
        return DisplayList(clients)

    def getPrimaryReferrerUID(self):
        primary_referrer = self.getPrimaryReferrer()
        if primary_referrer:
            return primary_referrer.UID()


# schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)


atapi.registerType(Doctor, PROJECTNAME)
