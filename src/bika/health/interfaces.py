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

from bika.lims.interfaces import IBikaLIMS
from senaite.impress.interfaces import ISenaiteImpressLayer
from senaite.lims.interfaces import ISenaiteLIMS
from zope.interface import Interface


class IBikaHealth(IBikaLIMS, ISenaiteLIMS, ISenaiteImpressLayer):
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
