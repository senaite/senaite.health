# -*- coding: utf-8 -*-

from bika.health.config import PROJECTNAME
from bika.lims import api
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.health import logger

version = "2.0.0"
profile = "profile-{0}:default".format(PROJECTNAME)

INSTALL_PRODUCTS = [
    "senaite.health",
]


@upgradestep(PROJECTNAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup  # noqa
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(PROJECTNAME)

    if ut.isOlderVersion(PROJECTNAME, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            PROJECTNAME, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(PROJECTNAME, ver_from,
                                                   version))

    # -------- ADD YOUR STUFF BELOW --------

    # Install the new SENAITE HEALTH package
    install_senaite_health(portal)

    logger.info("{0} upgraded to version {1}".format(PROJECTNAME, version))
    return True


def install_senaite_health(portal):
    """Install new SENAITE HEALTH Add-on
    """
    logger.info("Installing SENAITE HEALTH 2.x...")
    qi = api.get_tool("portal_quickinstaller")

    for p in INSTALL_PRODUCTS:
        if qi.isProductInstalled(p):
            continue
        logger.info("Installing '{}' ...".format(p))
        qi.installProduct(p)
    logger.info("Installing SENAITE HEALTH 2.x [DONE]")
