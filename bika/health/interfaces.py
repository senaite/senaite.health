# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.interface import Interface


class IBikaHealth(Interface):
    """Marker interface that defines a Zope 3 browser layer.
    A layer specific for this add-on product.
    This interface is referred in browserlayer.xml.
    All views and viewlets register against this layer will appear on
    your Plone site only when the add-on installer has been run.
    """

class IBikaHealthCatalogPatientListing(Interface):
   """
   """

class IPatient(Interface):
    """Patient"""

class IPatients(Interface):
    """Patient folder"""

class IDoctor(Interface):
    """Doctor"""

class IDoctors(Interface):
    """Doctor folder"""

class IDrugs(Interface):
    ""

class IDrugProhibitions(Interface):
    ""

class IImmunizations(Interface):
    ""

class ISymptoms(Interface):
    ""

class IDiseases(Interface):
    ""

class IAetiologicAgents(Interface):
    ""

class ITreatments(Interface):
    ""

class IVaccinationCenter(Interface):
    ""

class IVaccinationCenters(Interface):
    ""

class ICaseStatuses(Interface):
    ""

class ICaseOutcomes(Interface):
    ""

class ICaseSyndromicClassifications(Interface):
    ""

class IEpidemiologicalYears(Interface):
    ""

class IIdentifierTypes(Interface):
    ""

class IInsuranceCompany(Interface):
    ""

class IInsuranceCompanies(Interface):
    ""

class IEthnicity(Interface):
    """
    Ethnicity content type marker
    """


class IEthnicities(Interface):
    """
    Ethnicities content folder marker
    """
