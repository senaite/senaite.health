from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """ Issue #679: Add sort indexes for Batch object listings
    """
    portal = aq_parent(aq_inner(tool))
    bpc = getToolByName(portal, 'bika_patient_catalog')
    bpc.addIndex('inactive_state', 'FieldIndex')
    bpc.clearFindAndRebuild()
