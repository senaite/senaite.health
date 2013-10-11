from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore import permissions
from bika.lims.permissions import *

from Products.CMFCore.utils import getToolByName


def upgrade(tool):

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    try:
        wf = portal.portal_workflow
        setup.runImportStepFromProfile('profile-bika.health:default', 'workflow-csv')
        wf.updateRoleMappings()
    except:
        return False

    try:
        """ Reload jsregistry
        """
        setup.runImportStepFromProfile('profile-bika.health:default', 'jsregistry')
    except:
        return False

    return True
