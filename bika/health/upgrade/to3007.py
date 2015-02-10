from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.health.permissions import AddInsuranceCompany, ViewInsuranceCompanies
from bika.lims import logger

def upgrade(tool):
    """ Create InsuranceCompany content type.
    """
    portal = aq_parent(aq_inner(tool))
    typestool = getToolByName(portal, 'portal_types')

    # Re-run conf files where changes have been made.
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.health:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.health:default', 'controlpanel')
    setup.runImportStepFromProfile('profile-bika.health:default', 'factorytool')
    setup.runImportStepFromProfile('profile-bika.health:default', 'propertiestool')
    setup.runImportStepFromProfile('profile-bika.health:default', 'workflow')

    # Adding insurance companies in bika_setup
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('InsuranceCompany', ['bika_setup_catalog'])
    # If the type is not created yet, we should create it
    if not portal['bika_setup'].get('bika_insurancecompanies'):
        typestool.constructContent(type_name="InsuranceCompanies",
                                   container=portal['bika_setup'],
                                   id='bika_insurancecompanies',
                                   title='Insurance Companies')
    obj = portal['bika_setup']['bika_insurancecompanies']
    obj.unmarkCreationFlag()
    obj.reindexObject()
    if not portal['bika_setup'].get('bika_insurancecompanies'):
        logger.info("InsuranceCompanies not created")

    # Define permissions
    mp = portal.manage_permission
    mp(AddInsuranceCompany, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(ViewInsuranceCompanies, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'RegulatoryInspector'], 1)

    return True
