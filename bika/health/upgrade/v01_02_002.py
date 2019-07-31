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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.health import logger
from bika.health.config import PROJECTNAME
from bika.lims import api
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.2.2'
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
    setup.runImportStepFromProfile(profile, 'workflow')

    apply_doctor_permissions_for_clients(portal, ut)

    logger.info("{0} upgraded to version {1}".format(PROJECTNAME, version))
    return True


def apply_doctor_permissions_for_clients(portal, ut):
    workflow_tool = api.get_tool("portal_workflow")
    workflow = workflow_tool.getWorkflowById('bika_doctor_workflow')
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
