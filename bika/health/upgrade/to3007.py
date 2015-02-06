from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.health.permissions import ViewPatients, EditPatient, ViewAnalysisRequests, ViewSamples, ViewBatches
from Products.CMFCore import permissions


def upgrade(tool):
    """Health-191: Giving patient view permissions to client contacts contact
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    # Reloading patient workflow permissions
    setup.runImportStepFromProfile('profile-bika.health:default', 'workflow')
    setup.runImportStepFromProfile('profile-bika.health:default', 'workflow-csv')

    workflow = getToolByName(portal, 'portal_workflow')
    workflow.updateRoleMappings()

    # Adding client permissions to allow client contacts to see patients
    mp = portal.clients.manage_permission
    mp(ViewPatients, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'Client', 'RegulatoryInspector', 'Client'], 1)
    portal.clients.reindexObject()

    # Adding patients permissions to allow client contacts to see patients
    mp = portal.patients.manage_permission
    mp(EditPatient, ['Manager', 'LabManager', 'LabClerk', 'Client'], 1)
    mp(ViewPatients, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'RegulatoryInspector', 'Client'], 1)
    mp(ViewAnalysisRequests, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor', 'Client'], 0)
    mp(ViewSamples, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor', 'Client'], 0)
    mp(ViewBatches, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor', 'Client'], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor', 'Client'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor', 'Client'], 0)
    portal.patients.reindexObject()

    # Rewriting in order to see the label with vew permissions
    client = portal.portal_types.getTypeInfo("Client")
    client.addAction(id="patients",
        name="Patients",
        action="string:${object_url}/patients",
        permission="BIKA: View Patients",
        category="object",
        visible=True,
        icon_expr="string:${portal_url}/images/patient.png",
        link_target="",
        description="",
        condition="")

    return True
