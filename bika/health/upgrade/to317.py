from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.health.permissions import AddEthnicity, ViewEthnicities
from bika.lims import logger


def upgrade(tool):

    # Adding bika.health.analysisrequest.ar_add_health_standard.js
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    typestool = getToolByName(portal, 'portal_types')

    # reread jsregistry with the new data
    setup.runImportStepFromProfile('profile-bika.health:default', 'jsregistry')
    # Reread cssregistry to update the changes
    setup.runImportStepFromProfile('profile-bika.health:default', 'cssregistry')
    # Reread typeinfo to update/add the modified/added types
    setup.runImportStepFromProfile('profile-bika.health:default', 'typeinfo')
    # Reread factorytool to add the the new ethnicity type
    setup.runImportStepFromProfile('profile-bika.health:default', 'factorytool')
    # Reread workflow to add the the new ethnicity type
    setup.runImportStepFromProfile('profile-bika.health:default', 'workflow')
    # Reread controlpanel to add the the new ethnicity type
    setup.runImportStepFromProfile('profile-bika.health:default', 'controlpanel')

    # Adding Ethnicity roles
    workflow = getToolByName(portal, 'portal_workflow')
    workflow.updateRoleMappings()

    # Adding Ethnicity content type
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('Ethnicity', ['bika_setup_catalog', ])
    # If the type is not created yet, we should create it
    if not portal['bika_setup'].get('bika_ethnicities'):
        typestool.constructContent(type_name="Ethnicities",
                                   container=portal['bika_setup'],
                                   id='bika_ethnicities',
                                   title='Ethnicity')
    obj = portal['bika_setup']['bika_ethnicities']
    obj.unmarkCreationFlag()
    obj.reindexObject()
    if not portal['bika_setup'].get('bika_ethnicities'):
        logger.info("Ethnicities not created")

    # Define permissions for ethnicity
    mp = portal.manage_permission
    mp(AddEthnicity, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(ViewEthnicities, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'RegulatoryInspector'], 1)

    return True
