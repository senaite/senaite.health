from Acquisition import aq_inner
from Acquisition import aq_parent

def upgrade(tool):

    # Adding bika.health.analysisrequest.ar_add_health_standard.js

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    # reread jsregistry with the new data
    setup.runImportStepFromProfile('profile-bika.health:default', 'jsregistry')

    return True

