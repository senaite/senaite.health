from Acquisition import aq_inner
from Acquisition import aq_parent

def upgrade(tool):
    """ JS changes
        HEALTH-223
        This upgrade step registers the new js controller related with doctors.
    """

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # reread jsregistry with the new data
    setup.runImportStepFromProfile('profile-bika.health:default', 'jsregistry')

    return True

