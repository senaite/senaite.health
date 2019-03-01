# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it"s authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from App.class_init import InitializeClass
from bika.health.interfaces import IBikaHealthCatalogPatientListing
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_COLUMNS
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_INDEXES
from zope.interface import implements

CATALOG_PATIENTS = "bikahealth_catalog_patient_listing"

CATALOG_TYPES = [
    "Patients",
]

CATALOG_INDEXES = {
    "client_assigned": "BooleanIndex",
    "client_uid": "FieldIndex",
    "getClientPatientID": "FieldIndex",
    # TODO Replace getFullName by Title
    "getFullname": "FieldIndex",
    "getPatientID": "FieldIndex",
    # TODO Remove in favour of client_uid
    "getPrimaryReferrerUID": "FieldIndex",
    "searchable_text": "TextIndexNG3",
}

CATALOG_COLUMNS = [
    # Columns with index counterpart
    "getClientPatientID",
    "getPatientID",
    "getPrimaryReferrerUID",

    # Columns without index counterpart
    "getAgeSplittedStr",
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


class BikaHealthCatalogPatientListing(BikaCatalogTool):
    """
    Catalog to list patients in BikaListing
    """
    implements(IBikaHealthCatalogPatientListing)

    def __init__(self):
        BikaCatalogTool.__init__(
            self, CATALOG_PATIENTS,
            "Senaite Health Catalog Patients",
            "BikaHealthCatalogPatientListing")


InitializeClass(BikaHealthCatalogPatientListing)
