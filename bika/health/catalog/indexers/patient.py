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

from bika.health.catalog.patient_catalog import CATALOG_PATIENTS
from bika.health.interfaces import IPatient
from bika.lims import api
from plone.indexer import indexer

@indexer(IPatient)
def searchable_text(instance):
    """ Retrieves all the values of metadata columns in the catalog for
    wildcard searches
    :return: all metadata values joined in a string
    """
    entries = []
    catalog = api.get_tool(CATALOG_PATIENTS)
    columns = catalog.schema()
    brains = catalog({"UID": api.get_uid(instance)})
    brain = brains[0] if brains else None
    for column in columns:
        brain_value = api.safe_getattr(brain, column, None)
        instance_value = api.safe_getattr(instance, column, None)
        parsed = api.to_searchable_text_metadata(brain_value or instance_value)
        entries.append(parsed)

    # Concatenate all strings to one text blob
    return " ".join(entries)


@indexer(IPatient)
def client_uid(instance):
    """Returns the uid of the Client assigned to the Patient, if any. Otherwise
    returns "-1".
    """
    client = instance.getClient()
    if client:
        return api.get_uid(client)
    return "-1"


@indexer(IPatient)
def client_assigned(instance):
    """Returns whether the Patient belongs to a Client or not
    """
    if instance.getClient():
        return True
    return False
