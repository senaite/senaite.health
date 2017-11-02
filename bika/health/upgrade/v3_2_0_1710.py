# This file is part of Bika Health
#
# Copyright 2011-2017 by its authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent

from bika.health import logger
from bika.health.interfaces import IPatient
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from plone.api.portal import get_tool
from Products.CMFCore.permissions import ModifyPortalContent
from bika.health.catalog import CATALOG_PATIENT_LISTING

product = 'bika.health'
version = '3.2.0.1710'


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    ut = UpgradeUtils(portal)
    ufrom = ut.getInstalledVersion(product)
    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ufrom, version))
        # The currently installed version is more recent than the target
        # version of this upgradestep
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ufrom, version))

    # Allow Client Contacts to Add Patients
    roles = ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector',
             'Doctor', 'Client']
    pm = portal.patients.manage_permission
    pm(ModifyPortalContent, roles, 0)

    # Allow Client Contacts to Edit Patients
    wf_tool = get_tool('portal_workflow')
    workflow = wf_tool.getWorkflowById('bika_patient_workflow')
    state = workflow.states['active']
    state.permission_roles[ModifyPortalContent] = tuple(roles)

    # Update role mappings for previously created patients
    for patient in portal.patients:
        if IPatient.providedBy(patient):
            workflow.updateRoleMappingsFor(patient)

    # Reindex patient catalog and bika catalog
    logger.info("Reindexing {0}, {1}".format(CATALOG_PATIENT_LISTING, 'bika_catalog'))
    ut.reindexcatalog[CATALOG_PATIENT_LISTING] = 'SearchableText'
    ut.reindexcatalog['bika_catalog'] = 'SearchableText'
    ut.refreshCatalogs()
    logger.info("Catalogs updated")

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True
