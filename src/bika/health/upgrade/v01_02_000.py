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
from bika.health.config import PROJECTNAME
from bika.health.setuphandlers import remove_action
from bika.health.setuphandlers import setup_content_actions
from bika.health.setuphandlers import setup_id_formatting
from bika.health.setuphandlers import setup_roles_permissions
from bika.health.upgrade.utils import del_column
from bika.health.upgrade.utils import del_index
from bika.health.upgrade.utils import setup_catalogs
from bika.lims import api
from bika.lims.api import security
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.upgrade.utils import commit_transaction

version = '1.2.0'
profile = 'profile-{0}:default'.format(PROJECTNAME)


CATALOGS_BY_TYPE = [
    # Tuples of (type, [catalog])
]

INDEXES = [
    # Tuples of (catalog, index_name, index_type)
    (CATALOG_PATIENTS, "client_assigned", "BooleanIndex"),
    (CATALOG_PATIENTS, "client_uid", "FieldIndex"),
    (CATALOG_PATIENTS, "listing_searchable_text", "TextIndexNG3")
]

COLUMNS = [
    # Tuples of (catalog, column_name)
]

INDEXES_TO_DELETE = [
    # Tuples of (catalog, index_name)
    (CATALOG_PATIENTS, "getPatientIdentifiers"),
    (CATALOG_PATIENTS, "inactive_state"),
    (CATALOG_PATIENTS, "searchable_text")
]

COLUMNS_TO_DELETE = [
    # Tuples of (catalog, column_name)
    (CATALOG_PATIENTS, "getMobilePhone"),
    (CATALOG_PATIENTS, "getPhysicalPath"),
    (CATALOG_PATIENTS, "inactive_state"),
]

CSS_TO_REMOVE = [
    "++resource++bika.health.css/hide_contentmenu.css",
    "++resource++bika.health.css/hide_editable_border.css",
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
    setup.runImportStepFromProfile(profile, "browserlayer")
    setup.runImportStepFromProfile(profile, "typeinfo")
    setup.runImportStepFromProfile(profile, "skins")

    # Setup catalogs
    setup_catalogs(CATALOGS_BY_TYPE, INDEXES, COLUMNS)

    # Remove indexes and metadata columns
    remove_indexes_and_metadata()

    # Setup permissions
    setup_roles_permissions(portal)

    # Setup ID Formatting
    setup_id_formatting(portal)

    # Add "Patients" and "Doctors" action views in Client type
    setup_content_actions(portal)

    # Remove "Samples" action views from Doctors and Patients
    remove_sample_actions(portal)

    # Setup "Owner" roles for patients to client contacts
    setup_patients_ownership(portal)

    # Update workflows
    update_workflows(portal)

    # remove stale CSS
    remove_stale_css(portal)

    logger.info("{0} upgraded to version {1}".format(PROJECTNAME, version))
    return True


def remove_indexes_and_metadata():
    """Remove stale indexes and metadata from catalogs
    """
    for catalog, name in INDEXES_TO_DELETE:
        del_index(catalog, name)
    for catalog, name in COLUMNS_TO_DELETE:
        del_column(catalog, name)


def remove_sample_actions(portal):
    """Remove the "Sample" action view from inside Patient and Doctor objects
    """
    logger.info("Removing Samples action view from Patients ...")
    patient_type = portal.portal_types.getTypeInfo("Patient")
    remove_action(patient_type, "samples")

    logger.info("Removing Samples action view from Doctors ...")
    doctor_type = portal.portal_types.getTypeInfo("Doctor")
    remove_action(doctor_type, "samples")


def setup_patients_ownership(portal):
    """Set the role "Owner" to all the client contacts that belong to the same
    client as the patient, if any
    """
    logger.info("Applying Patients ownership ...")
    brains = api.search(dict(portal_type="Patient"), CATALOG_PATIENTS)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num % 100 == 0:
            logger.info("Applying Patients Ownership {}/{}".format(num, total))
        purge_owners_for(api.get_object(brain))

        if num % 1000 == 0:
            commit_transaction()
    commit_transaction()


def update_workflows(portal):
    """Updates the affected workflows
    """
    logger.info("Updating workflows ...")

    # Re-import rolemap and workflow tools
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "rolemap")
    setup.runImportStepFromProfile(profile, "workflow")

    # Update role mappings for Patient objects
    ut = UpgradeUtils(portal)
    ut.recursiveUpdateRoleMappings(portal.patients, commit_window=500)
    commit_transaction()


def remove_stale_css(portal):
    """Removes stale CSS
    """
    logger.info("Removing stale css ...")
    for css in CSS_TO_REMOVE:
        logger.info("Unregistering CSS %s" % css)
        portal.portal_css.unregisterResource(css)


# TODO: This is no longer needed!
def assign_owners_for(patient):
    """Assign the role "Owner" to the contacts of the client assigned to the
    patient passed in, if any
    """
    client = patient.getClient()
    if not client:
        return False

    contacts = client.objectValues("Contact")
    users = map(lambda contact: contact.getUser(), contacts)
    users = filter(None, users)
    for user in users:
        security.grant_local_roles_for(patient, roles=["Owner"], user=user)
    patient.reindexObjectSecurity()
    return True


def purge_owners_for(patient):
    """Remove role "Owner" from all those client contacts that do not belong to
    the same Client the patient is assigned to and assigns the role "Owner" to
    the client contacts assigned to the patient
    """
    # Add role "Owner" for this Patient to all contacts from this Client
    assign_owners_for(patient)

    # Unassign role "Owner" from contacts that belong to another Client
    patient_client = patient.getClient()
    patient_client_uid = patient_client and api.get_uid(patient_client) or None
    for client in api.search(dict(portal_type="Client"), "portal_catalog"):
        if api.get_uid(client) == patient_client_uid:
            continue

        client = api.get_object(client)
        contacts = client.objectValues("Contact")
        users = map(lambda contact: contact.getUser(), contacts)
        users = filter(None, users)
        for user in users:
            security.revoke_local_roles_for(patient, ["Owner"], user=user)
    patient.reindexObjectSecurity()
