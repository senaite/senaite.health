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

from bika.health import CATALOG_PATIENTS
from bika.health import api
from bika.health import DEFAULT_PROFILE_ID
from bika.health import logger
from bika.health.config import PROJECTNAME
from bika.health.setuphandlers import allow_patients_inside_clients
from bika.health.setuphandlers import setup_panic_alerts
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.upgrade.v01_03_003 import fix_email_address

version = '1.2.3'
profile = 'profile-{0}:default'.format(PROJECTNAME)

# List of javascripts to unregister
JAVASCRIPTS_TO_REMOVE = [
    "++resource++bika.health.js/bika.health.analysisrequest.add.js",
    "++resource++bika.health.js/bika.health.doctor.js",
    "++resource++bika.health.js/bika.health.analysisrequest.ar_add_health_standard.js",
    "++resource++bika.health.js/utils.js",
    "++resource++bika.health.js/doctor.js",
    "++resource++bika.health.js/client.js",
    "++resource++bika.health.js/bika.health.analysisrequest_add.js",
    "++resource++bika.health.js/bika.health.patient_edit.js",
    "++resource++bika.health.js/bika.health.batch_view.js",
    "++resource++bika.health.js/bika.health.batch_edit.js",
    "++resource++bika.health.js/bika.health.bikasetup_edit.js",
    "++resource++bika.health.js/bika.health.client_edit.js",
]

# List of css to unregister
CSS_TO_REMOVE = [
    "bika_health_standard_analysis_request.css",
]

# Metadata from catalogs to remove
METADATA_TO_REMOVE = [
    # AgeSplittedStr was only used in patients listing
    # https://github.com/senaite/senaite.health/pull/180
    (CATALOG_PATIENTS, "getAgeSplittedStr"),
]


@upgradestep(PROJECTNAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(PROJECTNAME)

    if ut.isOlderVersion(PROJECTNAME, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            PROJECTNAME, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(PROJECTNAME, ver_from,
                                                   version))

    # -------- ADD YOUR STUFF BELOW --------
    setup.runImportStepFromProfile(DEFAULT_PROFILE_ID, "skins")    
    setup.runImportStepFromProfile(DEFAULT_PROFILE_ID, "jsregistry")

    # Install senaite.panic add-on if not yet installed
    install_senaite_panic(portal)
    
    # Setup template text for panic level alert emails
    # https://github.com/senaite/senaite.health/pull/161
    setup_panic_alerts(portal)

    # Update Sample's PanicEmailAlertSent field
    # https://github.com/senaite/senaite.health/pull/161
    update_sample_panic_alert_field(portal)

    # Allow Patient content type inside Client
    # Note: this should always be run if core's typestool is reimported
    allow_patients_inside_clients(portal)

    # Remove stale javascripts
    remove_stale_javascripts(portal)

    # Remove stale css
    remove_stale_css(portal)

    # Fix email addresses
    # https://github.com/senaite/senaite.health/pulls/172
    fix_health_email_addresses(portal)

    # Remove stale catalog columns
    remove_stale_metadata(portal)

    logger.info("{0} upgraded to version {1}".format(PROJECTNAME, version))
    return True


def update_sample_panic_alert_field(portal):
    """The behavior of the AnalysisRequest's field `PanicEmailAlertToClientSent`
    from senaite.health is replaced by senaite.panic's PanicEmailAlertSent
    """
    logger.info("Updating Sample's PanicEmailAlertSent field ...")
    query = dict(portal_type="AnalysisRequest",
                 sort_on="created",
                 sort_order="descending")
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Updating PanicEmailAlertSent field: {}/{}"
                        .format(num, total))
        sample = api.get_object(brain)
        if sample.__dict__.get("PanicEmailAlertToClientSent", False):
            sample.setPanicEmailAlertSent(True)

    logger.info("Updating Sample's PanicEmailAlertSent field [DONE]")


def remove_stale_javascripts(portal):
    """Removes stale javascripts
    """
    logger.info("Removing stale javascripts ...")
    for js in JAVASCRIPTS_TO_REMOVE:
        logger.info("Unregistering JS %s" % js)
        portal.portal_javascripts.unregisterResource(js)

    logger.info("Removing stale javascripts [DONE]")


def remove_stale_css(portal):
    """Removes stale CSS
    """
    logger.info("Removing stale css ...")
    for css in CSS_TO_REMOVE:
        logger.info("Unregistering CSS %s" % css)
        portal.portal_css.unregisterResource(css)


def fix_health_email_addresses(portal):
    """Validates the email address for portal types that inherit from Person.
    The field did not have an email validator, causing some views to fail when
    rendering the value while expecting a valid email address format
    """
    # Fix email address for portal types from portal_catalog
    portal_types = ["VaccinationCenterContact", "Doctor"]
    fix_email_address(portal, portal_types=portal_types)

    # Fix email address for portal types from other catalogs
    portal_types = ["Patient"]
    fix_email_address(portal, portal_types=portal_types,
                      catalog_id=CATALOG_PATIENTS)


def install_senaite_panic(portal):
    """Install the senaite.panic addon
    """
    qi = api.get_tool("portal_quickinstaller")
    profile = "senaite.panic"
    if profile not in qi.listInstallableProfiles():
        logger.error("Profile '{}' not found. Forgot to run buildout?"
                     .format(profile))
        return
    if qi.isProductInstalled(profile):
        logger.info("'{}' is installed".format(profile))
        return
    qi.installProduct(profile)


def remove_stale_metadata(portal):
    logger.info("Removing stale metadata ...")
    for catalog, column in METADATA_TO_REMOVE:
        del_metadata(catalog, column)
    logger.info("Removing stale metadata ... [DONE]")


def del_metadata(catalog_id, column):
    logger.info("Removing '{}' metadata from '{}' ..."
                .format(column, catalog_id))
    catalog = api.get_tool(catalog_id)
    if column not in catalog.schema():
        logger.info("Metadata '{}' not in catalog '{}' [SKIP]"
                    .format(column, catalog_id))
        return
    catalog.delColumn(column)
