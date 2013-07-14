from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import *
from Products.CMFCore import permissions


def upgrade(tool):
    """ Lab Clerk should not see any result
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    wftool = portal.portal_workflow

    # Modified permissions of patient workflow
    setup.runImportStepFromProfile('profile-bika.health:default', 'workflow-csv')
    wftool.updateRoleMappings()

    return True
