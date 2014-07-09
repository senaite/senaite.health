from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    #Adding getGender element
    portal = aq_parent(aq_inner(tool))
    bsc = getToolByName(portal, 'bika_setup_catalog')
    addIndexAndColumn(bsc, 'getGender', 'FieldIndex')
    bsc.clearFindAndRebuild()

    return True

def addIndexAndColumn(catalog, index, indextype):
    try:
        catalog.addIndex(index, indextype)
    except:
        pass
    try:
        catalog.addColumn(index)
    except:
        pass

