from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.health.permissions import AddEthnicity


def upgrade(tool):

    # Adding bika.health.analysisrequest.ar_add_health_standard.js
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # reread jsregistry with the new data
    setup.runImportStepFromProfile('profile-bika.health:default', 'jsregistry')
    # Reread cssregistry to update the changes
    setup.runImportStepFromProfile('profile-bika.health:default', 'cssregistry')
    # Reread typeinfo to update/add the modified/added types
    setup.runImportStepFromProfile('profile-bika.health:default', 'typeinfo')

    # Adding Ethnicity roles
    workflow = getToolByName(portal, 'portal_workflow')
    workflow.updateRoleMappings()

    # Adding Ethnicity content type
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('Ethnicity', ['bika_setup_catalog', ])

    # Define permissions for ethnicity
    mp = portal.manage_permission
    mp(AddEthnicity, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)

    return True
