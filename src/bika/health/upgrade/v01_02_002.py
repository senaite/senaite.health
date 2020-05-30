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

import time

from Acquisition import aq_inner
from Products.CMFPlone.utils import _createObjectByType

from bika.health import CATALOG_PATIENTS
from bika.health import logger
from bika.health.config import PROJECTNAME
from bika.health.setuphandlers import allow_patients_inside_clients
from bika.health.utils import move_obj
from bika.lims import api
from bika.lims.catalog.bika_catalog import BIKA_CATALOG
from bika.lims.idserver import renameAfterCreation
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.utils import tmpID

version = '1.2.2'
profile = 'profile-{0}:default'.format(PROJECTNAME)

# List of javascripts to unregister
JAVASCRIPTS_TO_REMOVE = [
    "++resource++bika.health.js/bika.health.analysisrequest.add.js",
    "++resource++bika.health.js/bika.health.doctor.js",
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
    setup.runImportStepFromProfile(profile, "typeinfo")
    setup.runImportStepFromProfile(profile, "controlpanel")
    setup.runImportStepFromProfile(profile, 'rolemap')
    setup.runImportStepFromProfile(profile, 'workflow')

    apply_doctor_permissions_for_clients(portal, ut)

    # IdentifierType is no longer provided by core, but this content type is
    # still used in health to provide additional identification criteria for
    # Patients (e.g. drive license, passport, etc.)
    # https://github.com/senaite/senaite.core/pull/1430
    # https://github.com/senaite/senaite.health/pull/144
    restore_identifier_types(portal)

    # Move Patients with client assigned to Client folder
    # https://github.com/senaite/senaite.health/pull/152
    update_patients_role_mappings(portal)
    move_patients_to_clients(portal)

    # https://github.com/senaite/senaite.core/pull/1462
    remove_stale_javascripts(portal)

    logger.info("{0} upgraded to version {1}".format(PROJECTNAME, version))
    return True


def apply_doctor_permissions_for_clients(portal, ut):
    workflow_tool = api.get_tool("portal_workflow")
    workflow = workflow_tool.getWorkflowById('senaite_health_doctor_workflow')
    catalog = api.get_tool('portal_catalog')

    brains = catalog(portal_type='Doctor')
    counter = 0
    total = len(brains)
    logger.info(
        "Changing permissions for doctor objects: {0}".format(total))
    for brain in brains:
        obj = api.get_object(brain)
        workflow.updateRoleMappingsFor(obj)
        obj.reindexObject()
        counter += 1
        if counter % 100 == 0:
            logger.info(
                "Changing permissions for doctor objects: " +
                "{0}/{1}".format(counter, total))
    logger.info(
        "Changed permissions for doctor objects: " +
        "{0}/{1}".format(counter, total))


def restore_identifier_types(portal):
    """Restores the identifier types by using the values stored in patients
    """
    logger.info("Restoring additional identifiers for Patients ...")

    # Re-create the Identifier types folder in setup
    setup = api.get_setup()
    if "bika_identifiertypes" not in setup:
        obj = _createObjectByType("IdentifierTypes", setup, "bika_identifiertypes")
        obj.edit(title="Identifier Types")
        obj.unmarkCreationFlag()
        obj.reindexObject()

    # Infer the Identifier Types to be restored from Patients
    query = dict(portal_type="Patient")
    brains = api.search(query, CATALOG_PATIENTS)
    for brain in brains:
        ids = brain.getPatientIdentifiersStr
        if ids and ids not in [", "]:
            # Restore the IdentifierType by using the value stored in Patient
            obj = api.get_object(brain)
            restore_identifier_type(obj)


def restore_identifier_type(patient):
    """Restores the identifier types for the Patient passed in
    """
    patient_ids = patient.__dict__.get("PatientIdentifiers", [])
    for patient_id in patient_ids:
        identifier_id = patient_id.get("IdentifierType")
        id_value = patient_id.get("Identifier") or patient_id.get("value")
        if identifier_id and id_value:
            resolve_identifier_type(identifier_id)


def resolve_identifier_type(identifier_id):
    """Search for an identifier type with an ID that matches with the id
    passed in. If no identifier type is found, creates a new one
    """
    setup = api.get_setup()
    folder = setup.bika_identifiertypes
    id_types = folder.objectValues()
    for id_type in id_types:
        if api.get_title(id_type) == identifier_id:
            return id_type

    # Create a new identifier type
    logger.info("Creating new Identifier Type: {}".format(identifier_id))
    obj = _createObjectByType('IdentifierType', folder, tmpID())
    obj.edit(title=identifier_id, description=identifier_id)
    obj.unmarkCreationFlag()
    renameAfterCreation(obj)
    return obj


def update_patients_role_mappings(portal):
    """Updates the role mappings for patients folder cause we've changed the
    workflow bound to this type and we've added permission to Delete Objects
    """
    logger.info("Updating role mappings of patients folder ...")
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById("senaite_health_patients_workflow")
    workflow.updateRoleMappingsFor(portal.patients)
    portal.patients.reindexObject()
    logger.info("Updating role mappings of patients folder [DONE]")


def move_patients_to_clients(portal):
    """
    Moves patients with a Client assigned to the folder of the Client they
    belong to.
    """
    logger.info("Moving Patients inside Clients...")

    # We'll need this to update workflow mappings just after the move
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById("senaite_health_patient_workflow")

    # Allow Patient content type inside Clients
    allow_patients_inside_clients(portal)

    # Map patient uids against batches' clients
    patients_to_clients = dict()
    query = dict(portal_type="Batch")
    for batch_brain in api.search(query, BIKA_CATALOG):
        client_id = batch_brain.getClientID
        if not client_id:
            continue
        patient_uid = batch_brain.getPatientUID
        if not patient_uid:
            continue
        client_ids = patients_to_clients.get(patient_uid, [])
        client_ids.append(client_id)
        patients_to_clients[patient_uid] = list(set(client_ids))

    # Look through Patients and move them inside Clients
    start = time.time()
    clients_map = dict()
    patients_folder = portal.patients
    patients_origin = aq_inner(patients_folder)

    total = patients_folder.objectCount()
    for num, (p_id, patient) in enumerate(patients_folder.items()):
        if num and num % 100 == 0:
            end = time.time()
            logger.info("Moving Patients inside Clients: {}/{}: ({:.2f}s)"
                        .format(num, total, (end-start)))
            start = time.time()

        client_uid = patient.getField("PrimaryReferrer").getRaw(patient)
        if client_uid:
            # Update role mappings first (for workflow changes to take effect)
            workflow.updateRoleMappingsFor(patient)

            # Try to find out the Client from the Batch(es) assigned to patient
            client_ids = patients_to_clients.get(api.get_uid(patient), [])
            if len(client_ids) > 1:
                # Clinical Cases for this Patient belong to different clients,
                # so this Patient must remain not bound to any Client
                logger.warn("Patient with client assigned, but batches from "
                            "others: {}".format(p_id))

            else:
                client = clients_map.get(client_uid, None)
                if client is None:
                    client = api.get_object_by_uid(client_uid)
                    clients_map[client_uid] = client

                if client_ids and client_ids[0] != client.getClientID():
                    # Assigned client does not match with those from the batches
                    logger.warn("Patient with client assigned that does not "
                                "match with the client from batches: {}"
                                .format(p_id))

                else:
                    # Move Patient inside the client
                    #cp = patients_folder.manage_cutObjects(p_id)
                    #client.manage_pasteObjects(cp)
                    move_obj(patient, client)

    logger.info("Moving Patients inside Clients [DONE]")


def remove_stale_javascripts(portal):
    """Removes stale javascripts
    """
    logger.info("Removing stale javascripts ...")
    for js in JAVASCRIPTS_TO_REMOVE:
        logger.info("Unregistering JS %s" % js)
        portal.portal_javascripts.unregisterResource(js)

    logger.info("Removing stale javascripts [DONE]")
