# -*- coding: utf-8 -*-

from bika.health.setuphandlers import allow_doctors_inside_clients
from bika.health.setuphandlers import allow_patients_inside_clients
from bika.health.setuphandlers import reindex_content_structure
from bika.health.setuphandlers import setup_content_actions
from bika.health.setuphandlers import setup_ethnicities
from bika.health.setuphandlers import setup_health_catalogs
from bika.health.setuphandlers import setup_id_formatting
from bika.health.setuphandlers import setup_internal_clients
from bika.health.setuphandlers import setup_panic_alerts
from bika.health.setuphandlers import setup_roles_permissions
from bika.health.setuphandlers import setup_site_structure
from bika.health.setuphandlers import setup_user_groups
from bika.health.setuphandlers import setup_workflows
from bika.health.setuphandlers import sort_nav_bar
from plone.registry.interfaces import IRegistry
from senaite.health import logger
from zope.component import getUtility
from zope.interface import implementer

try:
    from Products.CMFPlone.interfaces import INonInstallable
except ImportError:
    from zope.interface import Interface

    class INonInstallable(Interface):
        pass

PROFILE_ID = "profile-senaite.health:default"
HEALTH_TYPES = [
    "AetiologicAgent",
    "AetiologicAgents",
    "CaseOutcome",
    "CaseOutcomes",
    "CaseStatus",
    "CaseStatuses",
    "CaseSyndromicClassification",
    "CaseSyndromicClassifications",
    "Disease",
    "Diseases",
    "Doctor",
    "Doctors",
    "Drug",
    "DrugProhibition",
    "DrugProhibitions",
    "Drugs",
    "Ethnicities",
    "Ethnicity",
    "IdentifierType",
    "IdentifierTypes",
    "Immunization",
    "Immunizations",
    "InsuranceCompanies",
    "InsuranceCompany",
    "Patient",
    "Patients",
    "Symptom",
    "Symptoms",
    "Treatment",
    "Treatments",
    "VaccinationCenter",
    "VaccinationCenterContact",
    "VaccinationCenters",
]


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
    _run_import_step(portal, "typeinfo")
    _run_import_step(portal, "factorytool")
    _run_import_step(portal, "workflow")
    _run_import_step(portal, "content")

    # Run Installers
    setup_health_catalogs(portal)

    # Setup portal permissions
    setup_roles_permissions(portal)

    # Setup user groups (e.g. Doctors)
    setup_user_groups(portal)

    # Setup site structure
    setup_site_structure(context)

    # Setup content actions
    setup_content_actions(portal)

    # Setup ID formatting for Health types
    setup_id_formatting(portal)

    # Setup default ethnicities
    setup_ethnicities(portal)

    # Setup custom workflow(s)
    setup_workflows(portal)

    # Setup internal clients top-level folder
    setup_internal_clients(portal)

    # Sort navigation bar
    sort_nav_bar(portal)

    # Allow patients inside clients
    # Note: this should always be run if core's typestool is reimported
    allow_patients_inside_clients(portal)

    # Allow doctors inside clients
    # Note: this should always be run if core's typestool is reimported
    allow_doctors_inside_clients(portal)

    # Reindex the top level folder in the portal and setup to fix missing icons
    reindex_content_structure(portal)

    # When installing senaite health together with core, health's skins are not
    # set before core's, even if after-before is set in profiles/skins.xml
    # Ensure health's skin layer(s) always gets priority over core's
    _run_import_step(portal, "skins")

    # Setup default email body and subject for panic alerts
    setup_panic_alerts(portal)

    # setup navigation types to display
    setup_navigation_types(portal)

    logger.info("SENAITE HEALTH install handler [DONE]")


def _run_import_step(portal, name, profile="profile-bika.health:default"):
    """Helper to install a GS import step from the given profile
    """
    logger.info("*** Running import step '{}' from profile '{}' ***"
                .format(name, profile))
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, name)


def setup_navigation_types(portal):
    """Add additional types for navigation
    """
    registry = getUtility(IRegistry)
    key = "plone.displayed_types"
    display_types = registry.get(key, ())

    new_display_types = set(display_types)
    new_display_types.update(HEALTH_TYPES)
    registry[key] = tuple(new_display_types)


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

    logger.info("SENAITE HEALTH post install handler [DONE]")
