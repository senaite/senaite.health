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
from bika.health.config import PROJECTNAME
from bika.health.setuphandlers import setup_internal_clients
from bika.health.setuphandlers import sort_nav_bar
from bika.lims import api
from bika.lims.setuphandlers import reindex_content_structure
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

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

    # Setup internal clients top-level folder
    setup_internal_clients(portal)

    # Sort navigation bar
    sort_nav_bar(portal)

    # Reindex the top level folder in the portal and setup to fix missing icons
    reindex_content_structure(portal)

    # Hide Doctor items from navigation bar
    hide_doctors_from_navbar(portal)

    # Add batches action to Doctor
    setup.runImportStepFromProfile(profile, "typeinfo")
    sort_doctor_actions(portal)

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