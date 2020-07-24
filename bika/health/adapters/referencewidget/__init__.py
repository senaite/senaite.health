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
from bika.health.utils import get_client_from_chain
from bika.health.utils import is_external_client
from bika.health.utils import resolve_query_for_shareable
from bika.lims import api
from bika.lims.adapters.referencewidgetvocabulary import \
    DefaultReferenceWidgetVocabulary
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IReferenceWidgetVocabulary


class IReferenceWidgetAdapter(IReferenceWidgetVocabulary):
    """Marker interface for reference widget adapters
    """

    def is_supported(self):
        """Returns whether the current adapter supports the search
        """


class IExclusiveReferenceWidgetAdapter(IReferenceWidgetAdapter):
    """Marker interface for 'exclusive' reference widget adapters
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
    ]

    # Types that are widely shared, regardless of the client type
    widely_shared_types = [
        "AnalysisProfile",
        "AnalysisSpec",
        "ARTemplate",
        "SamplePoint",
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

    def is_supported(self):
        """Returns whether the adapter supports the portal_type from the query
        """
        query = self.get_baseline_query()
        portal_type = self.get_portal_type(query)
        return portal_type in self.client_aware_types

    def get_client_from_query(self, query, purge=False):
        """Resolves the client from the query passed-in
        """
        keys = ["getPrimaryReferrerUID", "getClientUID", "getParentUID", "UID"]
        for key in keys:
            uid = query.get(key)
            if not api.is_uid(uid) or uid == "0":
                continue
            client = api.get_object_by_uid(uid)
            if IClient.providedBy(client):
                if purge:
                    # Remove the key:value from the query
                    del(query[key])
                return client
        return None

    def get_baseline_query(self):
        """Returns the baseline query to work with
        """
        return super(ClientAwareReferenceWidgetAdapter, self).get_raw_query()

    def get_raw_query(self):
        """Returns the raw query to use for current search, based on the
        base query + update query
        """
        query = self.get_baseline_query()
        logger.info("===============================================")
        logger.info("Custom client-aware reference widget vocabulary")
        logger.info(repr(query))

        # Get the portal type from the query
        portal_type = self.get_portal_type(query)

        # Try to resolve the client from the query
        client = self.get_client_from_query(query, purge=True)

        # Resolve the client from the context chain
        client = get_client_from_chain(self.context) or client

        # Resolve the criteria for filtering
        criteria = {}

        if portal_type in self.widely_shared_types:

            # The portal type can be shared widely (e.g. Sample Type)
            criteria = self.resolve_query(portal_type, client, True)

        elif portal_type in self.internally_shared_types:

            # The portal type can be shared among internal clients (e.g Batch)
            criteria = resolve_query_for_shareable(portal_type, client)

        elif portal_type == "Client":

            # Special case, when the item to look for is a Client
            context_portal_type = api.get_portal_type(self.context)
            if context_portal_type in self.internally_shared_types:

                if client and is_external_client(client):
                    # Display only the current Client in searches
                    criteria = self.resolve_query(portal_type, client, False)

                else:
                    # Display all internal clients
                    internal_clients = api.get_portal().internal_clients
                    criteria = {
                        "path": {
                            "query": api.get_path(internal_clients),
                            "depth": 1
                        }
                    }

            else:
                # Display current client only (if client != None) or all them
                criteria = self.resolve_query(portal_type, client, False)

        elif client:
            # Portal type is not shareable in any way (e.g Contact)
            criteria = self.resolve_query(portal_type, client, False)

        query.update(criteria)
        logger.info(repr(query))
        logger.info("===============================================")
        return query

    def resolve_query(self, portal_type, client, share):
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
