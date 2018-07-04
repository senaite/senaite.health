# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore import permissions

from bika.health import logger
from bika.health.config import PROJECTNAME as product
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

    add_doctor_action_for_client(portal)
    ut.addIndex('portal_catalog', 'getPrimaryReferrerUID', 'FieldIndex')
    ut.refreshCatalogs()

    logger.info("{0} upgraded to version {1}".format(product, version))

    return True


def add_doctor_action_for_client(portal):
    # Add doctor action for client portal_type programmatically
    client = portal.portal_types.getTypeInfo("Client")
    for action in client.listActionInfos():
        if action.get('id', None) == 'doctors':
            logger.info("Already existing 'doctor' action for client portal_type")
            return None
    client.addAction(
        id="doctors",
        name="Doctor",
        action="string:${object_url}/doctors",
        permission=permissions.View,
        category="object",
        visible=True,
        icon_expr="string:${portal_url}/images/doctor.png",
        link_target="",
        description="",
        condition="")
    logger.info("'doctor' action for client portal_type added")
