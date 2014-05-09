from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    bc = getToolByName(portal, 'bika_catalog')
    addIndexAndColumn(bc, 'getClientTitle', 'FieldIndex')
    addIndexAndColumn(bc, 'getPatientID', 'FieldIndex')
    addIndexAndColumn(bc, 'getPatientUID', 'FieldIndex')
    addIndexAndColumn(bc, 'getPatientTitle', 'FieldIndex')
    addIndexAndColumn(bc, 'getDoctorID', 'FieldIndex')
    addIndexAndColumn(bc, 'getDoctorUID', 'FieldIndex')
    addIndexAndColumn(bc, 'getDoctorTitle', 'FieldIndex')
    addIndexAndColumn(bc, 'getClientPatientID', 'FieldIndex')
    bc.clearFindAndRebuild()

    pc = getToolByName(portal, 'portal_catalog')
    addIndexAndColumn(pc, 'getDoctorID', 'FieldIndex')
    addIndexAndColumn(pc, 'getDoctorUID', 'FieldIndex')
    pc.clearFindAndRebuild()

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
