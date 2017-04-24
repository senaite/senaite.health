# This file is part of Bika Health
#
# Copyright 2011-2017 by its authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.health import logger
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.health.catalog.patient_catalog import CATALOG_PATIENT_LISTING
import traceback
import sys
import transaction

product = 'bika.health'
version = '3.2.0.1704'


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

    # Adding SearchableText index to Patient listing catalog
    plc = getToolByName(portal, CATALOG_PATIENT_LISTING)
    ut.addIndex(plc, 'SearchableText', 'ZCTextIndex')

    # Refresh affected catalogs
    ut.refreshCatalogs()

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True
