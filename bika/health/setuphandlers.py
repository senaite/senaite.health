# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

""" Bika setup handlers. """

from Products.CMFCore import permissions
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from bika.health import logger
from bika.health.catalog \
    import getCatalogDefinitions as getCatalogDefinitionsHealth
from bika.health.catalog import getCatalogExtensions
from bika.health.config import PROJECTNAME as product
from bika.lims import api
from bika.lims.catalog \
    import getCatalogDefinitions as getCatalogDefinitionsLIMS
from bika.lims.catalog import setup_catalogs
from bika.lims.idserver import renameAfterCreation
from bika.lims.permissions import AddAnalysisRequest, AddBatch
from bika.lims.utils import tmpID


class Empty:
    pass


def setupEthnicities(bika_setup):
    """
    Creates standard ethnicities
    """
    ethnicities = ['Native American', 'Asian', 'Black', 'Native Hawaiian or Other Pacific Islander', 'White',
                   'Hispanic or Latino']
    for ethnicityName in ethnicities:
        folder = bika_setup.bika_ethnicities
        # Generating a temporal object
        _id = folder.invokeFactory('Ethnicity', id=tmpID())
        obj = folder[_id]
        # Setting its values
        obj.edit(title=ethnicityName,
                 description='')
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)
    logger.info("Standard ethnicities enabled")


def setupHealthVarious(context):
    """ Setup Bika site structure """

    if context.readDataFile('bika.health.txt') is None:
        return
    portal = context.getSite()

    # index objects - importing through GenericSetup doesn't
    for obj_id in (
                   'doctors',
                   'patients',
                   ):
        obj = portal._getOb(obj_id)
        obj.unmarkCreationFlag()
        obj.reindexObject()

    # same for objects in bika_setup
    bika_setup = portal._getOb('bika_setup')
    for obj_id in (
                   'bika_aetiologicagents',
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
                   'bika_ethnicities',
                   ):
        obj = bika_setup._getOb(obj_id)
        obj.unmarkCreationFlag()
        obj.reindexObject()

    # Move doctors and patients above Samples in nav
    portal.moveObjectToPosition('doctors', portal.objectIds().index('samples'))
    portal.moveObjectToPosition('patients', portal.objectIds().index('samples'))
    portal.moveObjectToPosition('batches', portal.objectIds().index('samples'))

    # Resort Invoices and AR Invoice (HEALTH-215) in navigation
    portal.moveObjectToPosition('invoices', portal.objectIds().index('supplyorders'))
    portal.moveObjectToPosition('arimports', portal.objectIds().index('referencesamples'))

    # Plone's jQuery gets clobbered when jsregistry is loaded.
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-plone.app.jquery:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-plone.app.jquerytools:default', 'jsregistry')

    # Load bika.lims js always before bika.health ones.
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')

    # Add patient action for client portal_type programmatically
    client = portal.portal_types.getTypeInfo("Client")
    client.addAction(id="patients",
        name="Patients",
        action="string:${object_url}/patients",
        permission="BIKA: View Patients",
        category="object",
        visible=True,
        icon_expr="string:${portal_url}/images/patient.png",
        link_target="",
        description="",
        condition="")

    # Add doctor action for client portal_type programmatically
    client = portal.portal_types.getTypeInfo("Client")
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

    setupEthnicities(bika_setup)


def setupHealthGroupsAndRoles(context):

    if context.readDataFile('bika.health.txt') is None:
        return
    portal = context.getSite()

    # add roles
    for role in (
                 'Doctor',
                 ):
        if role not in portal.acl_users.portal_role_manager.listRoleIds():
            portal.acl_users.portal_role_manager.addRole(role)
        portal._addRole(role)

    # Create groups
    portal_groups = portal.portal_groups

    if 'Doctors' not in portal_groups.listGroupIds():
        portal_groups.addGroup('Doctors', title="Doctors",
            roles=['Member', 'Doctor'])


def setupHealthCatalogs(context):
    # an item should belong to only one catalog.
    # that way looking it up means first looking up *the* catalog
    # in which it is indexed, as well as making it cheaper to index.

    if context.readDataFile('bika.health.txt') is None:
        return
    portal = context.getSite()

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

    # create lexicon
    wordSplitter = Empty()
    wordSplitter.group = 'Word Splitter'
    wordSplitter.name = 'Unicode Whitespace splitter'
    caseNormalizer = Empty()
    caseNormalizer.group = 'Case Normalizer'
    caseNormalizer.name = 'Unicode Case Normalizer'
    stopWords = Empty()
    stopWords.group = 'Stop Words'
    stopWords.name = 'Remove listed and single char words'
    elem = [wordSplitter, caseNormalizer, stopWords]
    zc_extras = Empty()
    zc_extras.index_type = 'Okapi BM25 Rank'
    zc_extras.lexicon_id = 'Lexicon'

    # bika_catalog
    bc = getToolByName(portal, 'bika_catalog', None)
    if bc == None:
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
    if pc == None:
        logger.warning('Could not find the portal_catalog tool.')
        return
    addIndex(pc, 'getDoctorID', 'FieldIndex')
    addIndex(pc, 'getDoctorUID', 'FieldIndex')
    addIndex(pc, 'getPrimaryReferrerUID', 'FieldIndex')
    addColumn(pc, 'getDoctorID')
    addColumn(pc, 'getDoctorUID')

    # bika_setup_catalog
    bsc = getToolByName(portal, 'bika_setup_catalog', None)
    if bsc == None:
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
    at.setCatalogsByType('CaseSyndromicClassification', ['bika_setup_catalog', ])
    at.setCatalogsByType('Ethnicity', ['bika_setup_catalog', ])

    addIndex(bsc,'getGender', 'FieldIndex')
    addColumn(bsc,'getGender')

    catalog_definitions_lims_health = getCatalogDefinitionsLIMS()
    catalog_definitions_lims_health.update(getCatalogDefinitionsHealth())
    # Updating health catalogs if there is any change in them
    setup_catalogs(
        portal, catalog_definitions_lims_health,
        catalogs_extension=getCatalogExtensions())


def post_install(portal_setup):
    """Runs after the last import step of the *default* profile

    This handler is registered as a *post_handler* in the generic setup profile

    :param portal_setup: SetupTool
    """
    logger.info("SENAITE Health post-install handler [BEGIN]")

    # When installing senaite health together with core, health's skins are not
    # set before core's, even if after-before is set in profiles/skins.xml
    # Ensure health's skin layer(s) always gets priority over core's
    profile = 'profile-{0}:default'.format(product)
    portal_setup.runImportStepFromProfile(profile, "skins")

    # Allow client contacts to list, add and edit batches (cases)
    # Since bika_batch_workflow lives in senaite and we don't have a workflow
    # definition here, we need to apply the permission changes against the
    # workflow manually
    apply_batch_permissions_for_clients(portal_setup)

    logger.info("SENAITE Health post-install handler [DONE]")


def setupHealthTestContent(context):
    """Setup custom content"""
    pass


def apply_batch_permissions_for_clients(portal):
    """Apply permissions for client contacts to bika_batch_workfklow, so they
    can list, add and edit Batches (Clinical Cases)
    """
    # Give permission to Client for listing batches and show the "Add" button
    add_permission_for_role(portal.batches, permissions.View, 'Client')
    add_permission_for_role(portal, AddBatch, 'Client')

    # Add client to permission-maps of bika_batch_workflow.
    # We don't want the client to be able to close and re-open batches, so these
    # permission mappings are only applied to "open" state (initial state)
    wfid = 'bika_batch_workflow'
    wfstate = 'open'
    perms = [ModifyPortalContent, permissions.View, AddAnalysisRequest]
    added = add_permissions_for_role_in_workflow(wfid, wfstate, ['Client'], perms)
    if not added:
        logger.info("No changes in {}. Skipping rolemapping".format(wfid))
        return

    # Redo the rolemapping for all batches that are open
    wtool = api.get_tool("portal_workflow")
    workflow = wtool.getWorkflowById(wfid)
    catalog = api.get_tool('bika_catalog')
    brains = catalog(portal_type='Batch', review_state=wfstate)
    counter = 0
    total = len(brains)
    logger.info(
        "Changing permissions for Batch objects: {0}".format(total))
    for brain in brains:
        obj = api.get_object(brain)
        workflow.updateRoleMappingsFor(obj)
        obj.reindexObject()
        counter += 1
        if counter % 100 == 0:
            logger.info(
                "Changing permissions for Batch objects: " +
                "{0}/{1}".format(counter, total))
    logger.info(
        "Changed permissions for Batch objects: " +
        "{0}/{1}".format(counter, total))


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


def add_permissions_for_role_in_workflow(wfid, wfstate, roles, permissions):
    """Adds the permissions passed in for the given roles and for the specified
    workflow and its state
    :param wfid: workflow id
    :param wfstate: workflow state
    :param roles: roles the permissions must be granted to
    :param permissions: permissions to be granted
    :return True if succeed, otherwise, False
    """
    wtool = api.get_tool("portal_workflow")
    workflow = wtool.getWorkflowById(wfid)
    if not workflow:
        return False
    state = workflow.states.get(wfstate, None)
    if not state:
        return False
    # Get the permission-roles that apply to this state
    added = False
    for permission in permissions:
        # Get the roles that applies for this permission
        permission_info = state.getPermissionInfo(permission)
        acquired = permission_info['acquired']
        st_roles = permission_info['roles']
        roles_to_add = filter(lambda role: role not in st_roles, roles)
        if not roles_to_add:
            logger.info("Permission {} already granted for roles {} and state "
                        "{} in {}".format(repr(permission), repr(roles),
                                        wfstate, wfid))
            continue

        logger.info("Adding roles {} to permission {} in {} with state {}"
                    .format(repr(roles), repr(permission), wfid, wfstate))
        st_roles.extend(roles_to_add)
        state.setPermission(permission, acquired, st_roles)
        added = True
    return added