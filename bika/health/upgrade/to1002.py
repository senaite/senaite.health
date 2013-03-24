from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore import permissions
from bika.health.permissions import *


def upgrade(tool):
    """ Upgrade health privileges
    """
    portal = aq_parent(aq_inner(tool))

    mp = portal.manage_permission
    mp(ViewBatches, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'RegulatoryInspector'], 1)
    mp(ViewSamples, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'RegulatoryInspector'], 1)
    mp(ViewAnalysisRequests, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'RegulatoryInspector'], 1)

    return True
