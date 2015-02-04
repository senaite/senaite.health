from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.health.permissions import AddInsuranceCompany
from zExceptions import BadRequest

def upgrade(tool):
    """ Add InsuranceCompany content type.
    """
    # Add insurance company in bika_setup_catalog
    portal = aq_parent(aq_inner(tool))
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('InsuranceCompany', ['bika_setup_catalog'])

    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'controlpanel')

    mp = portal.manage_permission
    mp(AddInsuranceCompany, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)

    try:
        import pdb;pdb.set_trace()
        #bika_setup = portal._getOb('bika_setup')
        #bsc = getToolByName(portal, 'bika_setup_catalog', None)
        #bsc.reindexObject()
        #portal.insurancecompany.reindexObjects()
        #obj = bika_setup._getOb('insurancecompany')
        #obj.unmarkCreationFlag()
        #obj.reindexObject()

    except BadRequest:
        # folder already exists
        pass

    return True
