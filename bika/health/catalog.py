from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.ZCatalog.ZCatalog import ZCatalog
from zope.interface import implements
from bika.health.interfaces import IBikaHealthCatalogPatientListing


# Using a variable to avoid plain strings in code
CATALOG_PATIENT_LISTING = 'bikahealth_catalog_patient_listing'

_catalogs_definition = {
    # This catalog contains the metacolumns to list patients in bikalisting
    CATALOG_PATIENT_LISTING: {
        'types':   ['Patient', ],
        'indexes': {
            'created': 'DateIndex',
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
            'Title',
            'review_state',
            'inactive_state',
            'getObjectWorkflowStates',
            'getPhysicalPath',  # (patient's absolute path)
            'getClientPatientID',
            'getPrimaryReferrerUID',
            'getPrimaryReferrerURL',
            'getPrimaryReferrerTitle',
            'getGender',
            'getBirthDate',
            'getAgeSplittedStr',  # (=AgeYMD)
            'getPatientIdentifiersStr',  # (PatientIdentifiers stringified)
            'getMobilePhone',
            'getCity',
            'getDistrict',
            'getPostalCode',
            'getCountry',
            'getCitizenship',
            'getPatientID',
            'getNumberOfSamples',  # (all Samples)
            'getNumberOfSamplesCancelled',  # (Cancelled Samples)
            # (Samples with at least one AnalysisRequest <= verified)
            'getNumberOfSamplesOngoing',
            # (Samples with at least one AnalysisRequest >= published)
            'getNumberOfSamplesPublished',
            'getRatioOfSamplesOngoing',  # (a String like 'ongoing/samples')
        ]
    }
}
# Defines the extension for catalogs created in Bika LIMS
_catalogs_extensions = {
}


def getCatalogDefinitions():
    """
    Returns a dictionary with catalog definitions
    """
    return _catalogs_definition


def getCatalogExtensions():
    """
    Returns a dictionary with catalog extensions
    """
    return _catalogs_extensions


def getCatalog(instance, field='UID'):
    """ Return the catalog which indexes objects of instance's type.
    If an object is indexed by more than one catalog, the first match
    will be returned.
    """
    uid = instance.UID()
    if 'workflow_skiplist' in instance.REQUEST \
            and [x for x in instance.REQUEST['workflow_skiplist']
                 if x.find(uid) > -1]:
        return None
    else:
        # grab the first catalog we are indexed in.
        # we're only indexed in one.
        at = getToolByName(instance, 'archetype_tool')
        plone = instance.portal_url.getPortalObject()
        catalog_name = instance.portal_type in at.catalog_map \
            and at.catalog_map[instance.portal_type][0] or 'portal_catalog'

        catalog = getToolByName(plone, catalog_name)
        return catalog


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
                                search_sub = True,
                                apply_func = indexObject)

InitializeClass(BikaPatientCatalog)


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
InitializeClass(BikaHealthCatalogPatientListing)
