from Acquisition import aq_inner
from Acquisition import aq_parent


def upgrade(tool):

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    try:
        setup.runImportStepFromProfile('profile-bika.health:default', 'typeinfo')
        setup.runImportStepFromProfile('profile-bika.health:default', 'workflow-csv')
    except:
        return False
