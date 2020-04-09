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

from App.class_init import InitializeClass
from bika.health.interfaces import IBikaHealthCatalogPatientListing
from bika.lims.catalog.base import BaseCatalog
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_COLUMNS
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_INDEXES
from zope.interface import implements

CATALOG_PATIENTS = "bikahealth_catalog_patient_listing"

CATALOG_TYPES = [
    "Patient",
]

CATALOG_INDEXES = {
    "client_assigned": "BooleanIndex",
    "client_uid": "FieldIndex",
    "getClientPatientID": "FieldIndex",
    # TODO Replace getFullName by Title
    "getFullname": "FieldIndex",
    # TODO Remove in favour of getId or id
    "getPatientID": "FieldIndex",
    # TODO Remove in favour of client_uid
    "getPrimaryReferrerUID": "FieldIndex",
    "listing_searchable_text": "TextIndexNG3",
}

CATALOG_COLUMNS = [
    # Columns with index counterpart
    "getClientPatientID",
    "getPatientID",
    "getPrimaryReferrerUID",

    # Columns without index counterpart
    "getBirthDate",
    "getGender",
    "getMenstrualStatus",
    "getPrimaryReferrerID",
    "getPrimaryReferrerURL",
    "getPrimaryReferrerTitle",
    "getPatientIdentifiersStr",
]

# Add basic indexes and columns
CATALOG_INDEXES.update(BASE_CATALOG_INDEXES.copy())
CATALOG_COLUMNS += BASE_CATALOG_COLUMNS

patient_catalog_definition = {
    CATALOG_PATIENTS: {
        "types": list(set(CATALOG_TYPES)),
        "indexes": CATALOG_INDEXES,
        "columns": list(set(CATALOG_COLUMNS)),
    }
}


class BikaHealthCatalogPatientListing(BaseCatalog):
    """
    Catalog to list patients in BikaListing
    """
    implements(IBikaHealthCatalogPatientListing)

    def __init__(self):
        BaseCatalog.__init__(
            self, CATALOG_PATIENTS,
            "Senaite Health Catalog Patients",
            "BikaHealthCatalogPatientListing")


InitializeClass(BikaHealthCatalogPatientListing)
