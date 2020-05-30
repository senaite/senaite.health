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

from Products.CMFCore import permissions

from bika.health import logger
from bika.health.config import PROJECTNAME as product
from bika.health.permissions import AddDoctor
from bika.health.utils import add_permission_for_role
from bika.lims import api
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.1.3'
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
    # Ensure health's skins have always priority over core's
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "skins")
    setup.runImportStepFromProfile(profile, 'workflow')
    setup.runImportStepFromProfile(profile, "typeinfo")

    # Allow clients to list, add and edit doctors
    apply_doctor_permissions_for_clients(portal, ut)

    logger.info("{0} upgraded to version {1}".format(product, version))

    return True


def apply_doctor_permissions_for_clients(portal, ut):
    # Add doctor action for client portal_type
    add_doctor_action_for_client(portal)

    # Allow client contacts to list/add/edit Doctors
    workflow_tool = api.get_tool("portal_workflow")
    workflow = workflow_tool.getWorkflowById('bika_doctor_workflow')
    catalog = api.get_tool('portal_catalog')

    # Adding new index and columns in portal_catalog for doctors
    ut.addIndexAndColumn('portal_catalog', 'allowedRolesAndUsers', 'FieldIndex')
    ut.addIndex('portal_catalog', 'getPrimaryReferrerUID', 'FieldIndex')

    brains = catalog(portal_type='Doctor')
    counter = 0
    total = len(brains)
    logger.info(
        "Changing permissions for doctor objects: {0}".format(total))
    for brain in brains:
        allowed = brain.allowedRolesAndUsers or []
        if 'Client' not in allowed:
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

    # Allowing client to view clients folder
    add_permission_for_role(portal.doctors, permissions.View, 'Client')
    add_permission_for_role(portal.doctors, AddDoctor, 'Client')


def add_doctor_action_for_client(portal):
    """
    Adds doctor action for client portal_type programmatically
    :param portal: The portal object
    :return: None
    """
    client = portal.portal_types.getTypeInfo("Client")
    for action in client.listActionInfos():
        if action.get('id', None) == 'doctors':
            logger.info("Already existing 'doctor' action for client portal_type")
            return None
    client.addAction(
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
    logger.info("'doctor' action for client portal_type added")
