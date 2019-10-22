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

import itertools

from Acquisition import aq_base
from Products.CMFCore import permissions
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import ListFolderContents
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName

from bika.health import logger
from bika.health.catalog import \
    getCatalogDefinitions as getCatalogDefinitionsHealth
from bika.health.catalog import getCatalogExtensions
from bika.health.config import DEFAULT_PROFILE_ID
from bika.health.permissions import ViewPatients
from bika.lims import api
from bika.lims.catalog import \
    getCatalogDefinitions as getCatalogDefinitionsLIMS
from bika.lims.catalog import setup_catalogs
from bika.lims.idserver import renameAfterCreation
from bika.lims.permissions import AddAnalysisRequest
from bika.lims.permissions import AddBatch
from bika.lims.utils import tmpID


class Empty(object):
    pass


ROLES = [
    # Tuple of (role, permissions)
    # NOTE: here we only expect permissions that belong to other products and
    #       plone, cause health-specific permissions for this role are
    #       explicitly set in profile/rolemap.xml
    ("Doctor", [View, AccessContentsInformation, ListFolderContents]),
    ("Client", [AddBatch])
]

GROUPS = [
    # Tuple of (group_name, roles_group
    ("Doctors", ["Member", "Doctor"], ),
]

ID_FORMATTING = [
    {
        # P000001, P000002
        "portal_type": "Patient",
        "form": "P{seq:06d}",
        "prefix": "patient",
        "sequence_type": "generated",
        "counter_type": "",
        "split_length": 1,
    }, {
        # D0001, D0002, D0003
        "portal_type": "Doctor",
        "form": "D{seq:04d}",
        "prefix": "doctor",
        "sequence_type": "generated",
        "counter_type": "",
        "split_length": 1,
    }
]


def post_install(portal_setup):
    """Runs after the last import step of the *default* profile
    This handler is registered as a *post_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("SENAITE Health post-install handler [BEGIN]")
    context = portal_setup._getImportContext(DEFAULT_PROFILE_ID)
    portal = context.getSite()
    # Setup catalogs
    # TODO use upgrade.utils.setup_catalogs instead!
    setup_health_catalogs(portal)

    # Setup portal permissions
    setup_roles_permissions(portal)

    # Setup user groups (e.g. Doctors)
    setup_user_groups(portal)

    # Setup site structure
    setup_site_structure(context)

    # Setup javascripts
    setup_javascripts(portal)

    # Setup content actions
    setup_content_actions(portal)

    # Setup ID formatting for Health types
    setup_id_formatting(portal)

    # Setup default ethnicities
    setup_ethnicities(portal)

    # Reindex the top level folder in the portal and setup to fix missing icons
    reindex_content_structure(portal)

    # When installing senaite health together with core, health's skins are not
    # set before core's, even if after-before is set in profiles/skins.xml
    # Ensure health's skin layer(s) always gets priority over core's
    portal_setup.runImportStepFromProfile(DEFAULT_PROFILE_ID, "skins")

    logger.info("SENAITE Health post-install handler [DONE]")


def setup_user_groups(portal):
    logger.info("Setup User Groups ...")
    portal_groups = portal.portal_groups
    for group_name, roles in GROUPS:
        if group_name not in portal_groups.listGroupIds():
            portal_groups.addGroup(group_name, title=group_name, roles=roles)
            logger.info("Group '{}' with roles '{}' added"
                        .format(group_name, ", ".join(roles)))
        else:
            logger.info("Group '{}' already exist [SKIP]".format(group_name))
    logger.info("Setup User Groups [DONE]")


def setup_roles_permissions(portal):
    """Setup the top-level permissions for new roles. The new role is added to
    the roles that already have the permission granted (acquire=1)
    """
    logger.info("Setup roles permissions ...")
    for role_name, permissions in ROLES:
        for permission in permissions:
            add_permission_for_role(portal, permission, role_name)

    # Add "Add AnalysisRequest" permission for Clients in base analysisrequests
    # This makes the "Add" button to appear in AnalysisRequestsFolder view
    analysis_requests = portal.analysisrequests
    add_permission_for_role(analysis_requests, AddAnalysisRequest, "Client")
    logger.info("Setup roles permissions [DONE]")


def add_permission_for_role(folder, permission, role):
    """Grants a permission to the given role and given folder
    :param folder: the folder to which the permission for the role must apply
    :param permission: the permission to be assigned
    :param role: role to which the permission must be granted
    :return True if succeed, otherwise, False
    """
    roles = filter(lambda perm: perm.get('selected') == 'SELECTED',
                   folder.rolesOfPermission(permission))
    roles = map(lambda perm_role: perm_role['name'], roles)
    if role in roles:
        # Nothing to do, the role has the permission granted already
        logger.info(
            "Role '{}' has permission {} for {} already".format(role,
                                                                repr(permission),
                                                                repr(folder)))
        return False
    roles.append(role)
    acquire = folder.acquiredRolesAreUsedBy(permission) == 'CHECKED' and 1 or 0
    folder.manage_permission(permission, roles=roles, acquire=acquire)
    folder.reindexObject()
    logger.info(
        "Added permission {} to role '{}' for {}".format(repr(permission), role,
                                                         repr(folder)))
    return True


def setup_ethnicities(portal):
    """
    Creates standard ethnicities
    """
    logger.info("Setup default ethnicities ...")
    ethnicities = ['Native American', 'Asian', 'Black',
                   'Native Hawaiian or Other Pacific Islander', 'White',
                   'Hispanic or Latino']
    folder = portal.bika_setup.bika_ethnicities
    for ethnicityName in ethnicities:
        _id = folder.invokeFactory('Ethnicity', id=tmpID())
        obj = folder[_id]
        obj.edit(title=ethnicityName,
                 description='')
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)
    logger.info("Setup default ethnicities [DONE]")


def setup_site_structure(context):
    """ Setup contents structure for health
    """
    if context.readDataFile('bika.health.txt') is None:
        return
    portal = context.getSite()
    logger.info("Setup site structure ...")

    # index objects - importing through GenericSetup doesn't
    for obj_id in ('doctors',
                   'patients', ):
        obj = portal._getOb(obj_id)
        obj.unmarkCreationFlag()
        obj.reindexObject()

    # same for objects in bika_setup
    bika_setup = portal.bika_setup
    for obj_id in ('bika_aetiologicagents',
                   'bika_analysiscategories',
                   'bika_drugs',
                   'bika_drugprohibitions',
                   'bika_diseases',
                   'bika_treatments',
                   'bika_immunizations',
                   'bika_vaccinationcenters',
                   'bika_casestatuses',
                   'bika_caseoutcomes',
                   'bika_identifiertypes',
                   'bika_casesyndromicclassifications',
                   'bika_insurancecompanies',
                   'bika_ethnicities',):
        obj = bika_setup._getOb(obj_id)
        obj.unmarkCreationFlag()
        obj.reindexObject()

    logger.info("Setup site structure [DONE]")


def setup_javascripts(portal):
    # Plone's jQuery gets clobbered when jsregistry is loaded.
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-plone.app.jquery:default',
                                   'jsregistry')
    setup.runImportStepFromProfile('profile-plone.app.jquerytools:default',
                                   'jsregistry')

    # Load bika.lims js always before bika.health ones.
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')


def setup_content_actions(portal):
    """Add "patients" and "doctors" action views inside Client view
    """
    logger.info("Setup content actions ...")
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
    logger.info("Setup content actions [DONE]")


def remove_action(type_info, action_id):
    """Removes the action id from the type passed in
    """
    actions = map(lambda action: action.id, type_info._actions)
    if action_id not in actions:
        return True
    index = actions.index(action_id)
    type_info.deleteActions([index])
    return remove_action(type_info, action_id)


def setup_health_catalogs(portal):
    # an item should belong to only one catalog.
    # that way looking it up means first looking up *the* catalog
    # in which it is indexed, as well as making it cheaper to index.
    def addIndex(cat, *args):
        try:
            cat.addIndex(*args)
        except:
            pass

    def addColumn(cat, col):
        try:
            cat.addColumn(col)
        except:
            pass

    logger.info("Setup catalogs ...")

    # bika_catalog
    bc = getToolByName(portal, 'bika_catalog', None)
    if not bc:
        logger.warning('Could not find the bika_catalog tool.')
        return
    addIndex(bc, 'getClientTitle', 'FieldIndex')
    addIndex(bc, 'getPatientID', 'FieldIndex')
    addIndex(bc, 'getPatientUID', 'FieldIndex')
    addIndex(bc, 'getPatientTitle', 'FieldIndex')
    addIndex(bc, 'getDoctorID', 'FieldIndex')
    addIndex(bc, 'getDoctorUID', 'FieldIndex')
    addIndex(bc, 'getDoctorTitle', 'FieldIndex')
    addIndex(bc, 'getClientPatientID', 'FieldIndex')
    addColumn(bc, 'getClientTitle')
    addColumn(bc, 'getPatientID')
    addColumn(bc, 'getPatientUID')
    addColumn(bc, 'getPatientTitle')
    addColumn(bc, 'getDoctorID')
    addColumn(bc, 'getDoctorUID')
    addColumn(bc, 'getDoctorTitle')
    addColumn(bc, 'getClientPatientID')

    # portal_catalog
    pc = getToolByName(portal, 'portal_catalog', None)
    if not pc:
        logger.warning('Could not find the portal_catalog tool.')
        return
    addIndex(pc, 'getDoctorID', 'FieldIndex')
    addIndex(pc, 'getDoctorUID', 'FieldIndex')
    addIndex(pc, 'getPrimaryReferrerUID', 'FieldIndex')
    addColumn(pc, 'getDoctorID')
    addColumn(pc, 'getDoctorUID')

    # bika_setup_catalog
    bsc = getToolByName(portal, 'bika_setup_catalog', None)
    if not bsc:
        logger.warning('Could not find the bika_setup_catalog tool.')
        return
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('Disease', ['bika_setup_catalog', ])
    at.setCatalogsByType('AetiologicAgent', ['bika_setup_catalog', ])
    at.setCatalogsByType('Treatment', ['bika_setup_catalog'])
    at.setCatalogsByType('Symptom', ['bika_setup_catalog'])
    at.setCatalogsByType('Drug', ['bika_setup_catalog'])
    at.setCatalogsByType('DrugProhibition', ['bika_setup_catalog'])
    at.setCatalogsByType('VaccinationCenter', ['bika_setup_catalog', ])
    at.setCatalogsByType('InsuranceCompany', ['bika_setup_catalog', ])
    at.setCatalogsByType('Immunization', ['bika_setup_catalog', ])
    at.setCatalogsByType('CaseStatus', ['bika_setup_catalog', ])
    at.setCatalogsByType('CaseOutcome', ['bika_setup_catalog', ])
    at.setCatalogsByType('IdentifierType', ['bika_setup_catalog', ])
    at.setCatalogsByType('CaseSyndromicClassification', ['bika_setup_catalog'])
    at.setCatalogsByType('Ethnicity', ['bika_setup_catalog', ])

    addIndex(bsc, 'getGender', 'FieldIndex')
    addColumn(bsc, 'getGender')

    catalog_definitions_lims_health = getCatalogDefinitionsLIMS()
    catalog_definitions_lims_health.update(getCatalogDefinitionsHealth())
    # Updating health catalogs if there is any change in them
    setup_catalogs(
        portal, catalog_definitions_lims_health,
        catalogs_extension=getCatalogExtensions())

    logger.info("Setup catalogs [DONE]")


def setup_id_formatting(portal, format=None):
    """Setup default ID Formatting for health content types
    """
    if not format:
        logger.info("Setup ID formatting ...")
        for formatting in ID_FORMATTING:
            setup_id_formatting(portal, format=formatting)
        logger.info("Setup ID formatting [DONE]")
        return

    bs = portal.bika_setup
    p_type = format.get("portal_type", None)
    if not p_type:
        return
    id_map = bs.getIDFormatting()
    id_format = filter(lambda idf: idf.get("portal_type", "") == p_type, id_map)
    if id_format:
        logger.info("ID Format for {} already set: '{}' [SKIP]"
                    .format(p_type, id_format[0]["form"]))
        return

    form = format.get("form", "")
    if not form:
        logger.info("Param 'form' for portal type {} not set [SKIP")
        return

    logger.info("Applying format '{}' for {}".format(form, p_type))
    ids = list()
    for record in id_map:
        if record.get('portal_type', '') == p_type:
            continue
        ids.append(record)
    ids.append(format)
    bs.setIDFormatting(ids)


def reindex_content_structure(portal):
    """Reindex contents generated by Generic Setup
    """
    logger.info("*** Reindex content structure ***")

    def reindex(obj, recurse=False):
        # skip catalog tools etc.
        if api.is_object(obj):
            obj.reindexObject()
        if recurse and hasattr(aq_base(obj), "objectValues"):
            map(reindex, obj.objectValues())

    setup = api.get_setup()
    setupitems = setup.objectValues()
    rootitems = portal.objectValues()

    for obj in itertools.chain(setupitems, rootitems):
        if not api.is_object(obj):
            continue
        logger.info("Reindexing {}".format(repr(obj)))
        reindex(obj)
