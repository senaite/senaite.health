# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.health import logger
from bika.health.catalog.patient_catalog import CATALOG_PATIENTS
from bika.health.config import PROJECTNAME as product
from bika.health.setuphandlers import setup_id_formatting
from bika.health.upgrade.utils import setup_catalogs, del_index, del_column
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.2.0'
profile = 'profile-{0}:default'.format(product)


CATALOGS_BY_TYPE = [
    # Tuples of (type, [catalog])
]

INDEXES = [
    # Tuples of (catalog, index_name, index_type)
    (CATALOG_PATIENTS, "client_assigned", "BooleanIndex"),
    (CATALOG_PATIENTS, "client_uid", "FieldIndex"),
    (CATALOG_PATIENTS, "searchable_text", "TextIndexNG3")
]

COLUMNS = [
    # Tuples of (catalog, column_name)
]

INDEXES_TO_DELETE = [
    # Tuples of (catalog, index_name)
    (CATALOG_PATIENTS, "getPatientIdentifiers"),
    (CATALOG_PATIENTS, "inactive_state"),
    (CATALOG_PATIENTS, "listing_searchable_text")
]

COLUMNS_TO_DELETE = [
    # Tuples of (catalog, column_name)
    (CATALOG_PATIENTS, "getMobilePhone"),
    (CATALOG_PATIENTS, "getPhysicalPath"),
    (CATALOG_PATIENTS, "inactive_state"),
]


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF BELOW --------
    setup.runImportStepFromProfile(profile, 'browserlayer')

    # Setup catalogs
    setup_catalogs(CATALOGS_BY_TYPE, INDEXES, COLUMNS)

    # Remove indexes and metadata columns
    remove_indexes_and_metadata(portal)

    # Setup ID Formatting
    setup_id_formatting(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def remove_indexes_and_metadata(portal):
    """Remove stale indexes and metadata from catalogs
    """
    for catalog, name in INDEXES_TO_DELETE:
        del_index(catalog, name)
    for catalog, name in COLUMNS_TO_DELETE:
        del_column(catalog, name)