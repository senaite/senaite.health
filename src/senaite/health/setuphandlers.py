# -*- coding: utf-8 -*-

from senaite.health import logger
from zope.interface import implementer
from bika.lims.setuphandlers import reindex_content_structure

try:
    from Products.CMFPlone.interfaces import INonInstallable
except ImportError:
    from zope.interface import Interface

    class INonInstallable(Interface):
        pass

PROFILE_ID = "profile-senaite.health:default"


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide all profiles from site-creation and quickinstaller (not ZMI)"""
        return [
            "bika.health:default",
        ]


def install(context):
    """Install handler
    """
    if context.readDataFile("senaite.health.txt") is None:
        return

    logger.info("SENAITE HEALTH install handler [BEGIN]")
    portal = context.getSite()  # noqa

    # Run required import steps
    _run_import_step(portal, "skins")
    _run_import_step(portal, "browserlayer")
    _run_import_step(portal, "rolemap")
    _run_import_step(portal, "toolset")  # catalogs
    _run_import_step(portal, "catalog")
    _run_import_step(portal, "workflow")

    # Run required import steps
    setup_content_types(portal)
    setup_content_structure(portal)

    # Run Installers

    logger.info("SENAITE HEALTH install handler [DONE]")


def setup_content_types(portal):
    """Install AT content type information
    """
    logger.info("*** Install SENAITE HEALTH Content Types ***")
    _run_import_step(portal, "typeinfo")
    _run_import_step(portal, "factorytool")


def setup_content_structure(portal):
    """Install the base content structure
    """
    logger.info("*** Install SENAITE HEALTH Content Types ***")
    _run_import_step(portal, "content")
    reindex_content_structure(portal)


def _run_import_step(portal, name, profile="profile-bika.health:default"):
    """Helper to install a GS import step from the given profile
    """
    logger.info("*** Running import step '{}' from profile '{}' ***"
                .format(name, profile))
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, name)


def pre_install(portal_setup):
    """Runs berfore the first import step of the *default* profile

    This handler is registered as a *pre_handler* in the generic setup profile

    :param portal_setup: SetupTool
    """
    logger.info("SENAITE HEALTH pre-install handler [BEGIN]")

    # https://docs.plone.org/develop/addons/components/genericsetup.html#custom-installer-code-setuphandlers-py
    profile_id = PROFILE_ID
    context = portal_setup._getImportContext(profile_id)
    portal = context.getSite()  # noqa

    # Only install the health once!
    # qi = portal.portal_quickinstaller
    # if not qi.isProductInstalled("bika.lims"):
    #     portal_setup.runAllImportStepsFromProfile("profile-bika.lims:default")

    logger.info("SENAITE HEALTH pre-install handler [DONE]")


def post_install(portal_setup):
    """Runs after the last import step of the *default* profile

    This handler is registered as a *post_handler* in the generic setup profile

    :param portal_setup: SetupTool
    """
    logger.info("SENAITE HEALTH post install handler [BEGIN]")

    # https://docs.plone.org/develop/addons/components/genericsetup.html#custom-installer-code-setuphandlers-py
    profile_id = PROFILE_ID
    context = portal_setup._getImportContext(profile_id)
    portal = context.getSite()  # noqa

    from bika.health.setuphandlers import post_install
    post_install(portal_setup)

    logger.info("SENAITE HEALTH post install handler [DONE]")
