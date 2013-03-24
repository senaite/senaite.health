from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore import permissions
from bika.health.permissions import *


def upgrade(tool):
    """ Upgrade health privileges
    """
    portal = aq_parent(aq_inner(tool))

    mp = portal.manage_permission
    mp(AddAetiologicAgent, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddTreatment, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddDrug, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddImmunization, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddVaccinationCenter, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddSymptom, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddDrugProhibition, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)

    return True
