# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

""" Bika setup handlers. """

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.Permissions import AccessPreviousVersions
from Products.CMFEditions.Permissions import ApplyVersionControl
from Products.CMFEditions.Permissions import SaveNewVersion
from bika.health import logger
from bika.lims.catalog import setup_catalogs
from bika.lims.catalog\
    import getCatalogDefinitions as getCatalogDefinitionsLIMS
from bika.health.catalog\
    import getCatalogDefinitions as getCatalogDefinitionsHealth
from bika.health.catalog import getCatalogExtensions
from bika.lims.utils import tmpID
from bika.lims.idserver import renameAfterCreation
from bika.health.permissions import AddAetiologicAgent
from bika.health.permissions import ManageDoctors
from bika.health.permissions import ViewPatients
from bika.health.permissions import ViewBatches
from bika.health.permissions import ViewSamples
from bika.health.permissions import ViewAnalysisRequests
from bika.health.permissions import ViewInsuranceCompanies
from bika.health.permissions import ViewEthnicities
from bika.health.permissions import AddAetiologicAgent
from bika.health.permissions import AddDoctor
from bika.health.permissions import AddDrug
from bika.health.permissions import AddDrugProhibition
from bika.health.permissions import AddImmunization
from bika.health.permissions import AddPatient
from bika.health.permissions import AddSymptom
from bika.health.permissions import AddTreatment
from bika.health.permissions import AddVaccinationCenter
from bika.health.permissions import AddInsuranceCompany
from bika.health.permissions import AddEthnicity
from bika.health.permissions import EditPatient
from bika.health.permissions import ManageDoctors
from bika.lims.permissions import AddAnalysisRequest
from bika.lims.permissions import AddAnalysisSpec
from bika.lims.permissions import AddSample
from bika.lims.permissions import AddSamplePartition
from bika.lims.permissions import ManageAnalysisRequests
from bika.lims.permissions import ManageClients
from bika.lims.permissions import CancelAndReinstate


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
                   'bika_epidemiologicalyears',
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

    # if 'VaccinationCenters' not in portal_groups.listGroupIds():
    #     portal_groups.addGroup('VaccinationCenters', title="",
    #         roles=['Member', ])


def setupHealthPermissions(context):
    """ Set up some suggested role to permission mappings.
    New types and anything that differs from bika.lims gets specified here.
    These lines completely overwrite those in bika.lims - Changes common to
    both packages should be made in both places!
    """

    if context.readDataFile('bika.health.txt') is None:
        return
    portal = context.getSite()

    # Root permissions
    mp = portal.manage_permission
    mp(AddAnalysisRequest, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Doctor', 'Sampler'], 1)
    mp(AddSample, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Doctor', 'Sampler'], 1)
    mp(AddSamplePartition, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Doctor', 'Sampler'], 1)
    mp(AddDoctor, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddAetiologicAgent, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddTreatment, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddDrug, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddImmunization, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddVaccinationCenter, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddInsuranceCompany, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddSymptom, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddDrugProhibition, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddEthnicity, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)

    mp(ApplyVersionControl, ['Manager', 'LabManager', 'LabClerk', 'Doctor', 'Analyst', 'Owner', 'RegulatoryInspector'], 1)
    mp(SaveNewVersion, ['Manager', 'LabManager', 'LabClerk', 'Doctor', 'Analyst', 'Owner', 'RegulatoryInspector'], 1)
    mp(AccessPreviousVersions, ['Manager', 'LabManager', 'LabClerk', 'Doctor', 'Analyst', 'Owner', 'RegulatoryInspector'], 1)

    mp(ManageAnalysisRequests, ['Manager', 'LabManager', 'LabClerk', 'Doctor', 'Analyst', 'Sampler', 'Preserver', 'Owner', 'RegulatoryInspector'], 1)
    mp(ManageDoctors, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 1)

    mp(ViewBatches, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'RegulatoryInspector'], 1)
    mp(ViewSamples, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'RegulatoryInspector'], 1)
    mp(ViewAnalysisRequests, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'RegulatoryInspector'], 1)
    mp(ViewInsuranceCompanies, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'RegulatoryInspector'], 1)
    mp(ViewEthnicities, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'RegulatoryInspector'], 1)

    # /clients folder permissions
    # Member role must have view permission on /clients, to see the list.
    # This means within a client, perms granted on Member role are available
    # in clients not our own, allowing sideways entry if we're not careful.
    mp = portal.clients.manage_permission
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Member', 'LabClerk', 'Doctor', 'Analyst', 'Sampler', 'Preserver', 'RegulatoryInspector'], 0)
    mp(permissions.View,               ['Manager', 'LabManager', 'LabClerk', 'Doctor', 'Member', 'Analyst', 'Sampler', 'Preserver', 'RegulatoryInspector'], 0)
    mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Doctor', 'Analyst', 'Sampler', 'Preserver', 'Owner', 'RegulatoryInspector'], 0)
    mp(ManageClients, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector'], 0)
    mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
    mp(ViewPatients, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'Client', 'RegulatoryInspector'], 1)
    mp(AddAnalysisSpec, ['Manager', 'LabManager', 'Owner'], 0)
    portal.clients.reindexObject()

    for obj in portal.clients.objectValues():
        mp = obj.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Member', 'LabClerk', 'Doctor', 'Analyst', 'Sampler', 'Preserver', 'RegulatoryInspector'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Doctor', 'Member', 'Analyst', 'Sampler', 'Preserver', 'RegulatoryInspector'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Doctor', 'Analyst', 'Sampler', 'Preserver', 'Owner', 'RegulatoryInspector'], 0)
        obj.reindexObject()

    # /patients
    mp = portal.patients.manage_permission
    mp(AddPatient, ['Manager', 'LabManager', 'LabClerk', 'Client'], 1)
    mp(EditPatient, ['Manager', 'LabManager', 'LabClerk', 'Client'], 1)
    mp(ViewPatients, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'RegulatoryInspector', 'Client'], 1)
    mp(ViewAnalysisRequests, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor', 'Client'], 0)
    mp(ViewSamples, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor', 'Client'], 0)
    mp(ViewBatches, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor', 'Client'], 0)
    mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor', 'Client'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor', 'Client'], 0)
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor'], 0)
    mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'RegulatoryInspector', 'Doctor', 'Client'], 0)
    portal.patients.reindexObject()

    # /doctors
    mp = portal.doctors.manage_permission
    mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Doctor', 'Analyst', 'Sampler', 'Preserver', 'Owner'], 0)
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'LabTechnician', 'Doctor', 'Owner', 'Sampler', 'Preserver'], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'LabTechnician', 'Doctor', 'Owner', 'Sampler', 'Preserver'], 0)
    portal.doctors.reindexObject()

    # /reports folder permissions
    mp = portal.reports.manage_permission
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Member', 'LabClerk', 'Doctor'], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Doctor', 'Member'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Doctor', 'Owner'], 0)
    mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Doctor', 'Owner', 'Member'], 0)
    mp('ATContentTypes: Add Image', ['Manager', 'Labmanager', 'LabClerk', 'Doctor', 'Member', ], 0)
    mp('ATContentTypes: Add File', ['Manager', 'Labmanager', 'LabClerk', 'Doctor', 'Member', ], 0)
    portal.reports.reindexObject()


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
    at.setCatalogsByType('EpidemiologicalYear', ['bika_setup_catalog', ])
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


def setupHealthTestContent(context):
    """Setup custom content"""
    pass
