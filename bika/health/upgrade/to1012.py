from Acquisition import aq_inner
from Acquisition import aq_parent


def upgrade(tool):
    """ Reload jsregistry
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-bika.health:default', 'jsregistry')

    return True