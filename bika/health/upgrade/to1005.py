from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """ Issue #679: Add sort indexes for Batch object listings
    """
    portal = aq_parent(aq_inner(tool))
    bc = getToolByName(portal, 'bika_catalog')
    bc.addIndex('getPatientTitle', 'FieldIndex')
    bc.addIndex('getDoctorTitle', 'FieldIndex')
    bc.addIndex('getClientTitle', 'FieldIndex')
    bc.clearFindAndRebuild()
