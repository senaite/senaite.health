# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import time

import transaction
from Products.CMFCore import permissions
from bika.health import logger
from bika.health.catalog.patient_catalog import CATALOG_PATIENTS
from bika.health.config import PROJECTNAME
from bika.health.permissions import ViewPatients
from bika.health.setuphandlers import setup_id_formatting
from bika.health.subscribers.patient import purge_owners_for
from bika.health.upgrade.utils import setup_catalogs, del_index, del_column
from bika.lims import api
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.2.0'
profile = 'profile-{0}:default'.format(PROJECTNAME)


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

    # Setup catalogs
    setup_catalogs(CATALOGS_BY_TYPE, INDEXES, COLUMNS)

    # Remove indexes and metadata columns
    remove_indexes_and_metadata()

    # Setup ID Formatting
    setup_id_formatting(portal)

    # Add "Patients" and "Doctors" action views in Client type
    add_health_actions(portal)

    # Remove "Samples" action views from Doctors and Patients
    remove_sample_actions(portal)

    # Apply "Owner" roles for patients to client contacts
    apply_patients_ownership(portal)

    # Update workflows
    update_workflows(portal)

    logger.info("{0} upgraded to version {1}".format(PROJECTNAME, version))
    return True


def remove_indexes_and_metadata():
    """Remove stale indexes and metadata from catalogs
    """
    for catalog, name in INDEXES_TO_DELETE:
        del_index(catalog, name)
    for catalog, name in COLUMNS_TO_DELETE:
        del_column(catalog, name)


def add_health_actions(portal):
    """Add "patients" and "doctors" action views inside Client view
    """
    client_type = portal.portal_types.getTypeInfo("Client")

    remove_action(client_type, "patients")
    client_type.addAction(
        id="patients",
        name="Patients",
        action="string:${object_url}/patients",
        permission=ViewPatients,
        category="object",
        visible=True,
        icon_expr="string:${portal_url}/images/patient.png",
        link_target="",
        description="",
        condition="")

    remove_action(client_type, "doctors")
    client_type.addAction(
        id="doctors",
        name="Doctors",
        action="string:${object_url}/doctors",
        permission=permissions.View,
        category="object",
        visible=True,
        icon_expr="string:${portal_url}/images/doctor.png",
        link_target="",
        description="",
        condition="")


def remove_action(type_info, action_id):
    actions = map(lambda action: action.id, type_info._actions)
    if action_id not in actions:
        return True
    index = actions.index(action_id)
    type_info.deleteActions([index])
    return remove_action(type_info, action_id)


def remove_sample_actions(portal):
    """Remove the "Sample" action view from inside Patient and Doctor objects
    """
    logger.info("Removing Samples action view from Patients ...")
    patient_type = portal.portal_types.getTypeInfo("Patient")
    remove_action(patient_type, "samples")

    logger.info("Removing Samples action view from Doctors ...")
    doctor_type = portal.portal_types.getTypeInfo("Doctor")
    remove_action(doctor_type, "samples")


def apply_patients_ownership(portal):
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
    commit_transaction(portal)


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
    commit_transaction(portal)


def commit_transaction(portal):
    start = time.time()
    transaction.commit()
    end = time.time()
    logger.info("Commit transaction ... Took {:.2f}s".format(end - start))
