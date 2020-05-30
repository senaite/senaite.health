# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH.
#
# SENAITE.HEALTH is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.health import logger
from bika.health.catalog.patient_catalog import CATALOG_PATIENTS
from bika.health.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING

version = '1.1.2'
profile = 'profile-{0}:default'.format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF HERE --------
    ut.delIndexAndColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'getPatient')
    ut.delIndexAndColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'getDoctor')

    ut.addColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'getPatientID')
    ut.addIndexAndColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'getPatientTitle',
                         'FieldIndex')

    # In case if upgrade was already run after PR #72 got accepted
    ut.delColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'getPatientURL')
    ut.addColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'getPatientURL')
    ut.addColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'getClientPatientID')
    ut.addIndexAndColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'getDoctorTitle',
                         'FieldIndex')

    # In case if upgrade was already run after PR #72 got accepted
    ut.delColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'getDoctorURL')
    ut.addColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'getDoctorURL')
    ut.addIndex(CATALOG_PATIENTS, 'listing_searchable_text', 'TextIndexNG3')
    ut.refreshCatalogs()
    logger.info("{0} upgraded to version {1}".format(product, version))

    return True
