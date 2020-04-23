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
from bika.health import DEFAULT_PROFILE_ID
from bika.health import logger
from bika.health.config import PROJECTNAME
from bika.health.setuphandlers import allow_doctors_inside_clients
from bika.health.setuphandlers import allow_patients_inside_clients
from bika.health.setuphandlers import setup_internal_clients
from bika.health.setuphandlers import setup_user_groups
from bika.health.setuphandlers import sort_nav_bar
from bika.health.utils import is_internal_client
from bika.health.utils import move_obj
from bika.lims import api
from bika.lims.setuphandlers import reindex_content_structure
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.utils import changeWorkflowState

version = '1.2.4'
profile = 'profile-{0}:default'.format(PROJECTNAME)


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
    # Added action "batches" for Doctor type
    setup.runImportStepFromProfile(profile, "typeinfo")
    # Added InternalClient role
    setup.runImportStepFromProfile(DEFAULT_PROFILE_ID, "rolemap")
    # Added new state "shared" in patient_workflow, doctor_workflow
    setup.runImportStepFromProfile(DEFAULT_PROFILE_ID, "workflow")

    # Setup internal clients top-level folder
    setup_internal_clients(portal)

    # Sort navigation bar
    sort_nav_bar(portal)

    # Reindex the top level folder in the portal and setup to fix missing icons
    reindex_content_structure(portal)

    # Hide Doctor items from navigation bar
    hide_doctors_from_navbar(portal)

    # Add batches action to Doctor
    sort_doctor_actions(portal)

    # Setup groups (new group "InternalClient")
    setup_user_groups(portal)

    # Allow Patients and Doctors inside Clients
    allow_patients_inside_clients(portal)
    allow_doctors_inside_clients(portal)

    # Move doctors to clients
    move_doctors_to_clients(portal)

    logger.info("{0} upgraded to version {1}".format(PROJECTNAME, version))
    return True


def hide_doctors_from_navbar(portal):
    """Hide doctor items to be displayed in the navigation bar
    """
    logger.info("Hiding Doctors from navbar ...")

    # Plone uses exclude_from_nav metadata column to know if the object
    # has to be displayed in the navigation bar. This metadata column only
    # exists in portal_catalog and while with other portal types this might
    # not be required, this is necessary for Doctors, cause they are
    # stored in portal_catalog
    catalog = api.get_tool("portal_catalog")
    for doctor in portal.doctors.objectValues():
        # We don't need to reindex everything, but the metadata only. So we
        # just use any index
        catalog.reindexObject(doctor, idxs=["title"], update_metadata=1)

    logger.info("Hiding Doctors from navbar [DONE]")


def sort_doctor_actions(portal):
    """Sorts the actions list for Doctor
    """
    pt = api.get_tool("portal_types")
    type_info = pt.getTypeInfo("Doctor")
    sorted_actions = ["view", "edit", "analysisrequests", "batches", "access"]
    actions = type_info.listActions()
    actions = sorted(actions, key=lambda act: sorted_actions.index(act.id))
    type_info._actions = tuple(actions)


def move_doctors_to_clients(portal):
    """Moves the doctors into their assigned Client, if any
    """
    logger.info("Moving Doctors inside Clients...")
    query = {"portal_type": "Doctor"}
    doctors = map(api.get_object, api.search(query, "portal_catalog"))
    map(move_doctor_to_client, doctors)
    logger.info("Moving Doctors inside Clients [DONE]")


def move_doctor_to_client(doctor):
    """Moves a doctor to its assigned Client folder, if any
    """
    d_id = api.get_id(doctor)
    logger.info("Moving doctor {}".format(d_id))

    # Update role mappings first (for workflow changes to take effect)
    wf_tool = api.get_tool("portal_workflow")
    wf_id = "senaite_health_doctor_workflow"
    workflow = wf_tool.getWorkflowById(wf_id)
    workflow.updateRoleMappingsFor(doctor)

    # Do nothing if the doctor is not from inside /doctors
    portal = api.get_portal()
    doctors_folder = portal.doctors
    if doctor.aq_parent != doctors_folder:
        # The Doctor does not belong to doctors folder, do nothing
        return False

    # Resolve the client
    client = resolve_client_for_doctor(doctor)
    if not client or is_internal_client(client):
        # This doctor does not have a client assigned or an internal client, do
        # not move anywhere and make it shared
        status = api.get_review_status(doctor)
        if status not in ["shared", "inactive"]:
            changeWorkflowState(doctor, wf_id, "shared")
        return False

    # Move doctor inside the client
    client_id = api.get_id(client)
    logger.info("Moving doctor {} to {}".format(d_id, client_id))
    move_obj(doctor, doctors_folder)

    logger.info("Moving Doctors inside Clients [DONE]")


def resolve_client_for_doctor(doctor):
    # If the doctor has a client assigned already, return it directly. We
    # consider that a patient with a client assigned this way has been processed
    # already or does not require any further checks
    client = doctor.getClient()
    if client:
        return client

    # Try to infere the client from Samples or Batches
    batches = doctor.getBatches(full_objects=True)
    client_uids = map(lambda b: b.getClientUID(), batches)
    client_uids.extend(map(lambda s: s.getClientUID, doctor.getSamples()))
    client_uids = filter(None, list(set(client_uids)))
    if not client_uids:
        # This Doctor has no batch/sample assigned
        return None

    clients = map(api.get_object_by_uid, client_uids)
    internals = map(is_internal_client, clients)
    if all(internals):
        # All clients are internal, keep this Doctor without Client
        return None
    else:
        # OOps, we have a problem here. This Doctor is assigned to samples and
        # batches that belong to different types of client!
        logger.error("Doctor {} is assigned to clients from different types"
                     .format(api.get_id(doctor), repr(clients)))
        return None
