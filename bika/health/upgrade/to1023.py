from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.health.permissions import AddPatient, EditPatient, ViewPatients
from bika.lims import logger
from bika.lims.permissions import CancelAndReinstate
from Products.CMFCore.permissions import ListFolderContents, View,\
    AccessContentsInformation, ModifyPortalContent


def upgrade(tool):

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    wf = getToolByName(portal, 'portal_workflow')

    mp = portal.manage_permission
    mp(AddPatient, ['Manager', 'LabManager', 'LabClerk'], 1)
    mp(EditPatient, ['Manager', 'LabManager', 'LabClerk'], 1)
    mp(ViewPatients, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'RegulatoryInspector'], 1)
    portal.bika_setup.laboratory.reindexObject()

    mp = portal.patients.manage_permission
    mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
    mp(EditPatient, ['Manage', 'LabManager', 'LabClerk'], 0)
    mp(View, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor'], 0)
    mp(AccessContentsInformation, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor'], 0)
    mp(ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor'], 0)
    mp(ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor'], 0)
    portal.patients.reindexObject()
    
    setup.runImportStepFromProfile('profile-bika.health:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.health:default', 'workflow')
    setup.runImportStepFromProfile('profile-bika.health:default', 'workflow-csv')
    setup.runImportStepFromProfile('profile-bika.health:default', 'controlpanel')
    setup.runImportStepFromProfile('profile-bika.health:default', 'jsregistry')
    logger.info("Updating workflow role/permission mappings")
    wf.updateRoleMappings()
