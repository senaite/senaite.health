from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """ Add Client Patient ID indexes for searches
    """
    portal = aq_parent(aq_inner(tool))
    bc = getToolByName(portal, 'bika_catalog')
    bc.addIndex('getClientPatientID', 'FieldIndex')
    bc.clearFindAndRebuild()

    bpc = getToolByName(portal, 'bika_patient_catalog', None)
    bpc.addIndex('getClientPatientID', 'FieldIndex')
    bpc.addColumn('getClientPatientID')

    return True
