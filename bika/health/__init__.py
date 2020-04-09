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

from zope.i18nmessageid import MessageFactory
bikaMessageFactory = MessageFactory('senaite.health')
_ = MessageFactory('senaite.health')

import logging
logger = logging.getLogger('senaite.health')

from bika.health.validators import *
from bika.health.config import *
from bika.health import permissions
from Products.CMFCore.permissions import AddPortalContent

from AccessControl import allow_module
from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore import utils as plone_utils



# Make senaite.health modules importable by through-the-web
# https://docs.plone.org/develop/plone/security/sandboxing.html
# https://docs.zope.org/zope2/zdgbook/Security.html
# This allows Script python (e.g. guards from skins) to access to these modules.
# To provide access to a module inside of a package, we need to provide security
# declarations for all of the the packages and sub-packages along the path
# used to access the module. Thus, all the modules from the path passed in to
# `allow_module` will be available.
# TODO Check if we really need to allow utils module
allow_module('bika.health')
allow_module('bika.health.utils')


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
        perm_name = "Add{}".format(atype.portal_type)
        perm = getattr(permissions, perm_name, AddPortalContent)
        plone_utils.ContentInit(kind,
                          content_types      = (atype,),
                          permission         = perm,
                          extra_constructors = (constructor,),
                          fti                = ftis,
                          ).initialize(context)
