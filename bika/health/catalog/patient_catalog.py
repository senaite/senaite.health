# This file is part of Bika Health
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

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

# Using a variable to avoid plain strings in code
CATALOG_PATIENT_LISTING = 'bikahealth_catalog_patient_listing'

patient_catalog_definition = {
    # This catalog contains the metacolumns to list patients in bikalisting
    CATALOG_PATIENT_LISTING: {
        'types':   ['Patient', ],
        'indexes': {
            # Minimum indexes for bika_listing
            'id': 'FieldIndex',
            'created': 'DateIndex',
            # Necessary to avoid reindexing whole catalog when we need to
            # reindex only one object. ExtendedPathIndex also could be used.
            'path': 'PathIndex',
            'sortable_title': 'FieldIndex',
            'review_state': 'FieldIndex',
            'inactive_state': 'FieldIndex',
            'portal_type': 'FieldIndex',
            'UID': 'FieldIndex',
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
        },
        'columns': [
            'UID',
            'getId',
            'Title',
            'review_state',
            'inactive_state',
            'getObjectWorkflowStates',
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
    }
}


class BikaHealthCatalogPatientListing(CatalogTool):
    """
    Catalog to list patients in BikaListing
    """
    implements(IBikaHealthCatalogPatientListing)
    title = 'Bika Health Catalog Patients'
    id = CATALOG_PATIENT_LISTING
    portal_type = meta_type = 'BikaHealthCatalogPatientListing'
    plone_tool = 1
    security = ClassSecurityInfo()
    _properties = (
      {'id': 'title', 'type': 'string', 'mode': 'w'},)

    def __init__(self):
        ZCatalog.__init__(self, self.id)

    security.declareProtected(ManagePortal, 'clearFindAndRebuild')

    def clearFindAndRebuild(self):
        """Empties catalog, then finds all contentish objects (i.e. objects
           with an indexObject method), and reindexes them.
           This may take a long time.
        """
        def indexObject(obj, path):
            self.reindexObject(obj)
        logger.info('Cleaning and rebuilding %s...' % self.id)
        try:
            at = getToolByName(self, 'archetype_tool')
            types = [k for k, v in at.catalog_map.items()
                     if self.id in v]
            self.manage_catalogClear()
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portal.ZopeFindAndApply(
                portal,
                obj_metatypes=types,
                search_sub=True,
                apply_func=indexObject)
        except:
            logger.error(traceback.format_exc())
            e = sys.exc_info()
            logger.error(
                "Unable to clean and rebuild %s due to: %s" % (self.id, e))
        logger.info('%s cleaned and rebuilt' % self.id)


InitializeClass(BikaHealthCatalogPatientListing)


# TODO: Remove BikaPatientCatalog
# @deprecated(comment="bika.health.catalog.BikaPatientCatalog "
#                     "is deprecated and will be removed "
#                     "in Bika Health 3.3. Please, use "
#                     "BikaHealthCatalogPatientListing intead")
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
