# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

"""
"""
from Products.ATContentTypes.content import schemata
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.health.config import *
from bika.health.interfaces import IDoctor
from bika.health.permissions import *
from bika.lims.content.contact import Contact
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from zope.interface import implements

schema = Contact.schema.copy() + Schema((
    StringField('DoctorID',
        required=1,
        searchable=True,
        widget=StringWidget(
            label=_('Doctor ID'),
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

# schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(Doctor, PROJECTNAME)
