from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """ Add Client Patient ID
    """
    portal = aq_parent(aq_inner(tool))
    pc = getToolByName(portal, 'portal_catalog')
    proxies = pc(portal_type="Patient")
    pats = (proxy.getObject() for proxy in proxies)
    for patient in pats:
        patient.setClientPatientID('')

    return True