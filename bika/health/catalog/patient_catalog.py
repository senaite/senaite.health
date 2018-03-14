# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import sys
import traceback
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.ZCatalog.ZCatalog import ZCatalog
# Bika Health imports
from bika.health import logger
from bika.health.interfaces import IBikaHealthCatalogPatientListing
from bika.lims import deprecated
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_INDEXES
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_COLUMNS


# Using a variable to avoid plain strings in code
CATALOG_PATIENT_LISTING = 'bikahealth_catalog_patient_listing'
# Defining the indexes for this catalog
_indexes_dict = {
    'inactive_state': 'FieldIndex',
    # For quick-searches (search-box at the top-right), not for
    # embedded-code searches: the preferred way to get a Patient is
    # by using its UID.
    'getPatientID': 'FieldIndex',
    # (Client is also called PrimaryReferrer)
    'getPrimaryReferrerUID': 'FieldIndex',
    # (for partial/advanced searches!)
    'getFullname': 'FieldIndex',
    # (values from PatientIdentifiers field)
    'getPatientIdentifiers': 'KeywordIndex',
    'getClientPatientID': 'FieldIndex',
}
# Defining the columns for this catalog
_columns_list = [
    'inactive_state',
    'getPhysicalPath',  # (patient's absolute path)
    'getClientPatientID',
    'getPrimaryReferrerUID',
    'getPrimaryReferrerID',
    'getPrimaryReferrerURL',
    'getPrimaryReferrerTitle',
    'getGender',
    'getBirthDate',
    'getAgeSplittedStr',  # (=AgeYMD)
    'getPatientIdentifiersStr',  # (PatientIdentifiers stringified)
    'getMobilePhone',
    'getPatientID',
    'getMenstrualStatus',  # Review its use in ajaxGetPatientInfo
    # Columns with a function in Patient already in place below:
    # 'getNumberOfSamples',  # (all Samples)
    # 'getNumberOfSamplesCancelled',  # (Cancelled Samples)
    # # (Samples with at least one AnalysisRequest <= verified)
    # 'getNumberOfSamplesOngoing',
    # # (Samples with at least one AnalysisRequest >= published)
    # 'getNumberOfSamplesPublished',
    # 'getRatioOfSamplesOngoing',  # (a String like 'ongoing/samples')
]
# Adding basic indexes
_base_indexes_copy = BASE_CATALOG_INDEXES.copy()
_indexes_dict.update(_base_indexes_copy)
# Adding basic columns
_base_columns_copy = BASE_CATALOG_COLUMNS[:]
_columns_list += _base_columns_copy
# Defining the types for this catalog
_types_list = ['Patient', ]

patient_catalog_definition = {
    # This catalog contains the metacolumns to list patients in bikalisting
    CATALOG_PATIENT_LISTING: {
        'types': _types_list,
        'indexes': _indexes_dict,
        'columns': _columns_list,
    }
}


class BikaHealthCatalogPatientListing(BikaCatalogTool):
    """
    Catalog to list patients in BikaListing
    """
    implements(IBikaHealthCatalogPatientListing)

    def __init__(self):
        BikaCatalogTool.__init__(
            self, CATALOG_PATIENT_LISTING,
            'Bika Health Catalog Patients',
            'BikaHealthCatalogPatientListing')


InitializeClass(BikaHealthCatalogPatientListing)


# TODO: Remove BikaPatientCatalog
class BikaPatientCatalog(CatalogTool):

    """ Catalog for patients
    """
    security = ClassSecurityInfo()
    _properties = ({'id': 'title', 'type': 'string', 'mode': 'w'},)

    title = 'Bika Patient Catalog'
    id = 'bika_patient_catalog'
    portal_type = meta_type = 'BikaPatientCatalog'
    plone_tool = 1

    def __init__(self):
        ZCatalog.__init__(self, self.id)

    security.declareProtected(ManagePortal, 'clearFindAndRebuild')

    def clearFindAndRebuild(self):
        """
        """

        def indexObject(obj, path):
            self.reindexObject(obj)

        self.manage_catalogClear()
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal.ZopeFindAndApply(portal,
                                obj_metatypes=('Patient',),
                                search_sub=True,
                                apply_func=indexObject)
InitializeClass(BikaPatientCatalog)
