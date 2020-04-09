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

from bika.health.catalog.patient_catalog import CATALOG_PATIENTS
from bika.health.interfaces import IPatient
from bika.lims import api
from plone.indexer import indexer

@indexer(IPatient)
def listing_searchable_text(instance):
    """Fulltext search for the Patient
    """
    attributes = [
        "Title",
        "getFullname",
        "getId",
        "getPrimaryReferrerID",
        "getPrimaryReferrerTitle",
        "getClientPatientID",
        "getPatientIdentifiersStr"
    ]

    def get_value(instance, func_name):
        value = api.safe_getattr(instance, func_name, None)
        if not value:
            return None
        parsed = api.to_searchable_text_metadata(value)
        return parsed or None

    out_values = set()
    for attr in attributes:
        value = get_value(instance, attr)
        if value:
            out_values.add(value)

    return " ".join(out_values)

# TODO Remove Patient's client_uid indexer?
@indexer(IPatient)
def client_uid(instance):
    """Returns the uid of the Client assigned to the Patient, if any. Otherwise
    returns "-1".
    """
    client = instance.getClient()
    if client:
        return api.get_uid(client)
    return "-1"


# TODO Remove Patient's client_assigned indexer?
@indexer(IPatient)
def client_assigned(instance):
    """Returns whether the Patient belongs to a Client or not
    """
    if instance.getClient():
        return True
    return False
