# This file is part of Bika Health
#
# Copyright 2011-2017 by its authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore.utils import getToolByName
from bika.health import logger
from bika.health.catalog \
    import getCatalogDefinitions as getCatalogDefinitionsHealth, \
    getCatalogExtensions
from bika.lims.catalog \
    import getCatalogDefinitions as getCatalogDefinitionsLIMS
from bika.lims.catalog import setup_catalogs
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.upgrade.utils import migrate_to_blob

product = 'bika.health'
version = '3.2.0.1705'


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
    migrateFileFields(portal)

    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'toolset')

    # Adding colums and indexes if needed
    pc = getToolByName(portal, 'portal_catalog')
    # Updating lims catalogs if there is any change in them
    logger.info("Updating catalogs if needed...")
    catalog_definitions_lims_health = getCatalogDefinitionsLIMS()
    catalog_definitions_lims_health.update(getCatalogDefinitionsHealth())
    # Updating health catalogs if there is any change in them
    setup_catalogs(
        portal, catalog_definitions_lims_health,
        catalogs_extension=getCatalogExtensions())
    logger.info("Catalogs updated")

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def migrateFileFields(portal):
    """
    This function walks over all attachment types and migrates their FileField
    fields.
    """
    portal_types = [
        "Treatment"]
    for portal_type in portal_types:
        logger.info(
            "Starting migration of FileField fields from {}."
                .format(portal_type))
        # Do the migration
        migrate_to_blob(
            portal,
            portal_type=portal_type,
            remove_old_value=True)
        logger.info(
            "Finished migration of FileField fields from {}."
                .format(portal_type))
