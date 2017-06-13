# This file is part of Bika Health
#
# Copyright 2011-2017 by its authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent

from bika.health import logger
from bika.health.catalog import CATALOG_PATIENT_LISTING
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

product = 'bika.health'
version = '3.2.0.1706'


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

    # Updating lims catalogs if there is any change in them
    logger.info("Updating catalogs if needed...")
    patient_index_title(ut)
    ut.refreshCatalogs()
    logger.info("Catalogs updated")

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def patient_index_title(ut):
    """
    Moves the index 'title' to 'Title'
    """
    ut.delIndex(CATALOG_PATIENT_LISTING, 'title')
    ut.addIndex(
        CATALOG_PATIENT_LISTING, 'Title', 'FieldIndex'
    )
