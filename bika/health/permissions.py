# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

# Add Permissions
# ===============
# For "Add" permissions, keep the name of the variable as "Add<portal_type>".
# When the module gets initialized (bika.lims.__init__), the function initialize
# will look through these Add permissions attributes when registering types and
# will automatically associate them with their types.
AddAetiologicAgent = 'senaite.health: Add AetiologicAgent'
AddDoctor = 'senaite.health: Add Doctor'
AddDrug = 'senaite.health: Add Drug'
AddDrugProhibition = 'senaite.health: Add DrugProhibition'
AddEthnicity = 'senaite.health: Add Ethnicity'
AddImmunization = 'senaite.health: Add Immunization'
AddInsuranceCompany = 'senaite.health: Add InsuranceCompany'
AddPatient = 'senaite.health: Add Patient'
AddSymptom = 'senaite.health: Add Symptom'
AddTreatment = 'senaite.health: AddTreatment'
AddVaccinationCenter = 'senaite.health: Add VaccinationCenter'

# Transition permissions
# ======================
TransitionActivatePatient = "senaite.health: Transition: Activate Patient"
TransitionDeactivatePatient = "senaite.health: Transition: Deactivate Patient"


# Behavioral permissions
# ======================
ViewPatients = "senaite.health: View Patients"


ManageDoctors = "BIKA: Manage Doctors"

ViewBatches = "BIKA: View Batches"
ViewSamples = "BIKA: View Samples"
ViewAnalysisRequests = "BIKA: View AnalysisRequests"
ViewInsuranceCompanies = "BIKA: View InsuranceCompanies"
ViewEthnicities = "BIKA: View Ethnicities"

# Patient permissions
EditPatient = 'BIKA: Edit Patient'
