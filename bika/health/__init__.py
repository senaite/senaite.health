# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.i18nmessageid import MessageFactory
bikaMessageFactory = MessageFactory('bika.health')

import logging
logger = logging.getLogger('Bika Health')

from bika.lims.validators import *
from bika.health.validators import *
from bika.health.config import *
from bika.health.permissions import *

from AccessControl import ModuleSecurityInfo, allow_module
from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore import utils as plone_utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import ContentInit, ToolInit, getToolByName
from Products.CMFPlone import PloneMessageFactory
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.GenericSetup import EXTENSION, profile_registry

allow_module('AccessControl')
allow_module('bika.health')
allow_module('bika.lims')
allow_module('bika.lims.permissions')
allow_module('bika.lims.utils')
allow_module('bika.health.permissions')
allow_module('bika.health.utils')
allow_module('json')
allow_module('pdb')
allow_module('zope.i18n.locales')


def initialize(context):

    from content.aetiologicagent import AetiologicAgent
    from content.caseoutcome import CaseOutcome
    from content.casestatus import CaseStatus
    from content.ethnicity import Ethnicity
    from content.casesyndromicclassification import CaseSyndromicClassification
    from content.disease import Disease
    from content.doctor import Doctor
    from content.doctors import Doctors
    from content.drug import Drug
    from content.drugprohibition import DrugProhibition
    from content.epidemiologicalyear import EpidemiologicalYear
    from content.identifiertype import IdentifierType
    from content.immunization import Immunization
    from content.insurancecompany import InsuranceCompany
    from content.patient import Patient
    from content.patients import Patients
    from content.symptom import Symptom
    from content.treatment import Treatment
    from content.vaccinationcenter import VaccinationCenter
    from content.vaccinationcentercontact import VaccinationCenterContact

    from controlpanel.bika_aetiologicagents import AetiologicAgents
    from controlpanel.bika_caseoutcomes import CaseOutcomes
    from controlpanel.bika_casesyndromicclassifications import CaseSyndromicClassifications
    from controlpanel.bika_casestatuses import CaseStatuses
    from controlpanel.bika_diseases import Diseases
    from controlpanel.bika_drugprohibitions import DrugProhibitions
    from controlpanel.bika_drugs import Drugs
    from controlpanel.bika_epidemiologicalyears import EpidemiologicalYears
    from controlpanel.bika_identifiertypes import IdentifierTypes
    from controlpanel.bika_immunizations import Immunizations
    from controlpanel.bika_treatments import Treatments
    from controlpanel.bika_insurancecompanies import InsuranceCompanies
    from controlpanel.bika_ethnicities import Ethnicities
    from controlpanel.bika_vaccinationcenters import VaccinationCenters

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: Add %s" % (config.PROJECTNAME, atype.portal_type)
        perm = ADD_CONTENT_PERMISSIONS.get(atype.portal_type, ADD_CONTENT_PERMISSION)
        plone_utils.ContentInit(kind,
                          content_types      = (atype,),
                          permission         = perm,
                          extra_constructors = (constructor,),
                          fti                = ftis,
                          ).initialize(context)
