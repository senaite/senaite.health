from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import *
from Products.CMFCore import permissions


def upgrade(tool):
    """ https://github.com/bikalabs/Bika-LIMS/issues/703
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    wftool = portal.portal_workflow

    # funge existing (bika.lims) workflows to insert RegulatoryInspector
    # into their permission maps.  (except, skip these):
    skip_perms = ("Modify portal content", "BIKA: Publish")
    workflow = wftool.getWorkflowById('bika_batch_workflow')
    for state_id in ('open',
                     'sample_received',
                     'to_be_verified',
                     'verified',
                     'closed'):
        state = workflow.states[state_id]
        for perm in state.permission_roles.keys():
            roles = list(state.permission_roles[perm])
            if 'RegulatoryInspector' not in roles:
                roles.append('RegulatoryInspector')
                workflow.states[state_id].permission_roles[perm] = roles

    # Modified permissions of patient workflow
    setup.runImportStepFromProfile('profile-bika.health:default', 'workflow')
    wftool.updateRoleMappings()

    # Allow RegulatoryInspector to get into Clients
    mp = portal.clients.manage_permission
    mp(ManageClients, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector'], 1)
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Member', 'LabClerk', 'Doctor', 'Analyst', 'Sampler', 'Preserver', 'RegulatoryInspector'], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Doctor', 'Member', 'Analyst', 'Sampler', 'Preserver', 'RegulatoryInspector'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Doctor', 'Analyst', 'Sampler', 'Preserver', 'Owner', 'RegulatoryInspector'], 0)
    portal.clients.reindexObject()

    return True
