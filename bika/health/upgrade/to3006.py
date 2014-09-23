from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *

def upgrade(tool):
    """ JS changes
        HEALTH-150 Compatibility with the new JS loader machinery
    """

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # reread jsregistry with the new data
    setup.runImportStepFromProfile('profile-bika.health:default', 'jsregistry')

    return True
