from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    # Add drug in bika_setup_catalog
    portal = aq_parent(aq_inner(tool))
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('Drug', ['bika_setup_catalog'])

    # Update bika_setup_catalog with old portal_catalog's drugs
    pc = getToolByName(portal, 'portal_catalog', None)
    bsc = getToolByName(portal, 'bika_setup_catalog', None)
    lpc = pc(portal_type="Drug")    
    for obj in lpc:
        bsc.reindexObject(obj.getObject())

    return True
