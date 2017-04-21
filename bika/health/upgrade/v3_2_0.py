# This file is part of Bika Health LIS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.health import logger
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from Products.CMFCore import permissions
from bika.lims.catalog import setup_catalogs
from bika.lims.catalog\
    import getCatalogDefinitions as getCatalogDefinitionsLIMS
from bika.health.catalog\
    import getCatalogDefinitions as getCatalogDefinitionsHealth
from bika.health.catalog import getCatalogExtensions

product = 'bika.health'
version = '3.2.0'


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

    """Updated profile steps
    list of the generic setup import step names: portal.portal_setup.getSortedImportSteps() <---
    if you want more metadata use this: portal.portal_setup.getImportStepMetadata('jsregistry') <---
    important info about upgrade steps in
    http://stackoverflow.com/questions/7821498/is-there-a-good-reference-list-for-the-names-of-the-genericsetup-import-steps
    """
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.health:default', 'toolset')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'typeinfo')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'jsregistry')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'cssregistry')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'workflow-csv')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'factorytool')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'controlpanel')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'catalog')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'propertiestool')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'skins')
    """Update workflow permissions
    """
    # wf = getToolByName(portal, 'portal_workflow')
    # wf.updateRoleMappings()
    catalog_definitions_lims_health = getCatalogDefinitionsLIMS()
    catalog_definitions_lims_health.update(getCatalogDefinitionsHealth())
    # Updating health catalogs if there is any change in them
    setup_catalogs(
        portal, catalog_definitions_lims_health,
        catalogs_extension=getCatalogExtensions())
    # TODO: Deleting bika_patient_catalog
    # if 'bika_patient_catalog' in portal.keys():
    #     logger.info('Deletting catalog bika_patient_catalog...')
    #     portal.manage_delObjects(['bika_patient_catalog'])
    #     logger.info('Catalog bika_patient_catalog has been deleted')

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True
