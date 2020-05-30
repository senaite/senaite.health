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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.Archetypes import atapi
from Products.Archetypes.Field import ComputedField
from Products.Archetypes.Widget import ComputedWidget
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from zope.interface import implements

from bika.health import bikaMessageFactory as _
from bika.health.config import *
from bika.health.interfaces import IDoctor
from bika.lims import api
from bika.lims import idserver
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.content.contact import Contact
from bika.lims.interfaces import IClient

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
        allowed_types=('Client',),
        relationship='DoctorClient',
        required=1,
        widget=ReferenceWidget(
            label=_("Client"),
            size=30,
            catalog_name="portal_catalog",
            base_query={"is_active": True,
                        "sort_limit": 30,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            colModel=[
                {"columnName": "Title", "label": _("Title"),
                 "width": "30", "align": "left"},
                {"columnName": "getProvince", "label": _("Province"),
                 "width": "30", "align": "left"},
                {"columnName": "getDistrict", "label": _("District"),
                 "width": "30", "align": "left"}],
            showOn=True,
        ),
    ),
    ComputedField(
        'PrimaryReferrerID',
        expression="context.getClientID()",
        widget=ComputedWidget(
        ),
    ),
    ComputedField(
        'PrimaryReferrerTitle',
        expression="context.getClientTitle()",
        widget=ComputedWidget(
        ),
    ),
    ComputedField(
        'PrimaryReferrerUID',
        expression="context.getClientUID()",
        widget=ComputedWidget(
        ),
    ),
    ComputedField(
        'PrimaryReferrerURL',
        expression="context.getClientURL()",
        widget=ComputedWidget(
            visible=False
        ),
    ),
))

schema.moveField('PrimaryReferrer', before='Salutation')
schema.moveField('DoctorID', before='Salutation')


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

    def exclude_from_nav(self):
        """Returns True, to prevent Doctors to be displayed in the navbar
        """
        # Plone uses exclude_from_nav metadata column to know if the object
        # has to be displayed in the navigation bar. This metadata column only
        # exists in portal_catalog and while with other portal types this might
        # not be required, this is necessary for Doctors, cause they are
        # stored in portal_catalog
        return True

    getExcludeFromNav = exclude_from_nav

    def getClient(self):
        """Returns the client the Doctor is assigned to, if any
        """
        # The schema's field PrimaryReferrer is only used to allow the user to
        # assign the doctor to a client in edit form. The entered value is used
        # in ObjectModifiedEventHandler to move the doctor to the Client's
        # folder, so the value stored in the Schema's is not used anymore
        # See https://github.com/senaite/senaite.core/pull/152
        client = self.aq_parent
        if IClient.providedBy(client):
            return client
        return None

    def getClientID(self):
        """Returns the ID of the client this Patient belongs to or None
        """
        client = self.getClient()
        return client and api.get_id(client) or None

    def getClientUID(self):
        """Returns the UID of the client this Doctor is assigned to or None
        """
        client = self.getClient()
        return client and api.get_uid(client) or None

    def getClientURL(self):
        """Returns the URL of the client this Doctor is assigned to or None
        """
        client = self.getClient()
        return client and api.get_url(client) or None

    def getClientTitle(self):
        """Returns the title of the client this Doctor is assigned to or None
        """
        client = self.getClient()
        return client and api.get_title(client) or None

    def getSamples(self, **kwargs):
        """Return samples this Doctor is associated to
        """
        catalog = api.get_tool(CATALOG_ANALYSIS_REQUEST_LISTING, context=self)
        query = dict([(k, v) for k, v in kwargs.items()
                      if k in catalog.indexes()])
        query["getDoctorUID"] = api.get_uid(self)
        brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
        if not kwargs.get("full_objects", False):
            return brains
        return map(api.get_object, brains)

    def getBatches(self, **kwargs):
        """
        Returns the Batches this Doctor is assigned to
        """
        catalog = api.get_tool("bika_catalog")
        query = dict([(k, v) for k, v in kwargs.items()
                      if k in catalog.indexes()])
        query["getDoctorUID"] = api.get_uid(self)
        brains = api.search(query, "bika_catalog")
        if not kwargs.get("full_objects", False):
            return brains
        return map(api.get_object, brains)

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
