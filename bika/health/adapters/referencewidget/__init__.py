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

import six
from zope.interface import implements

from bika.health import logger
from bika.health.utils import is_internal_client
from bika.lims import api
from bika.lims.adapters.referencewidgetvocabulary import \
    DefaultReferenceWidgetVocabulary
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IReferenceWidgetVocabulary
from bika.lims.utils import chain
from bika.lims.utils import get_client


class IReferenceWidgetAdapter(IReferenceWidgetVocabulary):
    """Marker interface for reference widget adapters
    """


class ClientAwareReferenceWidgetAdapter(DefaultReferenceWidgetVocabulary):
    """Injects search criteria (filters) in the query when the current context
    is, belongs or is associated to a Client
    """
    implements(IReferenceWidgetAdapter)

    _client = None

    # portal_types that might be bound to a client
    client_aware_types = [
        "Batch",
        "Contact",
        "Client",
        "Doctor",
        "Patient",
        "AnalysisProfile",
        "AnalysisSpec",
        "ARTemplate",
        "SamplePoint",
        "SampleType",
    ]

    # Types that are widely shared, regardless of the client type
    widely_shared_types = [
        "AnalysisProfile",
        "AnalysisSpec",
        "ARTemplate",
        "SamplePoint",
        "SampleType",
    ]

    # Types that are shared, but when client is internal only
    internally_shared_types = [
        "Batch",
        "Patient",
        "Doctor",
    ]

    # Filtering indexes by type
    filter_indexes = [
        ("default", "getClientUID"),
        ("Client", "UID"),
        ("Contact", "getParentUID"),
    ]

    @property
    def client(self):
        """Returns the client the current context belongs to, by looking to
        the acquisition change only
        """
        if not self._client:
            for obj in chain(self.context):
                if IClient.providedBy(obj):
                    self._client = obj
                    break
        return self._client

    def get_raw_query(self):
        """Returns the raw query to use for current search, based on the
        base query + update query
        """
        logger.info("===============================================")
        logger.info("Custom client-aware reference widget vocabulary")
        query = super(ClientAwareReferenceWidgetAdapter, self).get_raw_query()

        # Get the portal types from the query
        portal_type = self.get_portal_type(query)
        if not portal_type:
            # Don't know the type we are searching for, do nothing
            return query

        if portal_type not in self.client_aware_types:
            # The portal type is not client aware, do nothing
            return query

        # Resolve the criteria for filtering
        criteria = {}

        if portal_type in self.widely_shared_types:
            # The portal type can be shared widely (e.g. Sample Type)
            if self.client:
                # Items from client + items without client
                criteria = self.resolve_query(portal_type, self.client, True)

            else:
                # Items without client
                criteria = self.resolve_query(portal_type, None, True)

        elif portal_type in self.internally_shared_types:
            # The portal type can be shared among internal clients (e.g Batch)
            if self.client and is_internal_client(self.client):
                # The client is internal. Can be shared
                # Items from client + items without client
                criteria = self.resolve_query(portal_type, self.client, True)

            elif self.client:
                # The client is external. Cannot be shared
                # Items from client
                criteria = self.resolve_query(portal_type, self.client, False)

            else:
                # Current context is outside a client
                # Items without client
                criteria = self.resolve_query(portal_type, None, True)

        elif portal_type == "Client":
            # Special case, when the item to look for is a Client
            context_portal_type = api.get_portal_type(self.context)
            if context_portal_type in self.internally_shared_types:
                # Current context can be shared internally (e.g. Batch)
                if self.client:
                    # Current context is inside a client
                    criteria = self.resolve_query(portal_type, self.client, False)
                else:
                    # Current context is outside a client
                    internal_clients = api.get_portal().internal_clients
                    criteria = {
                        "path": {
                            "query": api.get_path(internal_clients),
                            "depth": 1
                        }
                    }

            elif context_portal_type in self.widely_shared_types:
                # Current context can be shared widely (e.g Sample Type)
                if self.client:
                    # Current context is inside a client
                    criteria = self.resolve_query(portal_type, self.client, False)

        elif self.client:
            # Portal type is not shareable in any way (e.g Contact)
            criteria = self.resolve_query(portal_type, self.client, False)

        query.update(criteria)
        logger.info(repr(query))
        logger.info("===============================================")
        return query

    def resolve_query(self, portal_type, client, share):
        func_name = "resolve_query_for_{}".format(portal_type.lower())
        func = getattr(self, func_name, None)
        if func:
            return func(client, share)

        index = self.get_filter_index(portal_type)
        if not client:
            if share:
                return {index: ""}
            return {}

        # Filter by client
        uid = api.get_uid(client)
        if share:
            return {index: [uid, ""]}
        return {index: [uid]}

    def resolve_query_for_patient(self, client, share):
        if client and not share:
            return {"getPrimaryReferrerUID": api.get_uid(client)}
        patients = api.get_portal().patients
        return {"path": {"query": api.get_path(patients),
                         "depth": 1}}

    def get_filter_index(self, portal_type):
        indexes = dict(self.filter_indexes)
        index = indexes.get(portal_type)
        if not index:
            index = indexes.get("default")
        return index

    def get_portal_type(self, query):
        """Return the portal type from the query passed-in
        """
        portal_types = self.get_portal_types(query)
        if not portal_types:
            logger.warn("No portal types: {}".format(repr(portal_types)))
            return None

        if len(portal_types) > 1:
            logger.warn("Multiple portal types: {}".format(repr(portal_types)))
            return None

        return portal_types[0]

    def get_portal_types(self, query):
        """Return the list of portal types from the query passed-in
        """
        portal_types = query.get("portal_type", [])
        if isinstance(portal_types, six.string_types):
            portal_types = [portal_types]
        return portal_types
