from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """ HEALTH-105 Case syndromic classifications site eror in setup
    """
    portal = aq_parent(aq_inner(tool))
    portal_catalog = getToolByName(portal, 'portal_catalog')
    typestool = getToolByName(portal, 'portal_types')
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.health:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.health:default', 'controlpanel')
    setup.runImportStepFromProfile('profile-bika.health:default', 'factorytool')
    setup.runImportStepFromProfile('profile-bika.health:default', 'propertiestool')
    setup.runImportStepFromProfile('profile-bika.health:default', 'cssregistry')

    # Add CaseSyndromicClassification in bika_setup_catalog
    portal = aq_parent(aq_inner(tool))
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('CaseSyndromicClassification', ['bika_setup_catalog'])

    # Update bika_setup_catalog with old portal_catalog's CaseSyndr...
    pc = getToolByName(portal, 'portal_catalog', None)
    bsc = getToolByName(portal, 'bika_setup_catalog', None)
    lpc = pc(portal_type="CaseSyndromicClassification")
    for obj in lpc:
        bsc.reindexObject(obj.getObject())

    return True
