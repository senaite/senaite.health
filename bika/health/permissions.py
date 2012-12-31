"""All permissions are defined here.
They are also defined in permissions.zcml.
The two files must be kept in sync.

bika.health.__init__ imports * from this file, so
bika.health.PermName or bika.health.permissions.PermName are
both valid.

"""
from bika.health.permissions import *

# Add Permissions:
# ----------------
AddPatient = 'BIKA: Add Patient'
AddDoctor = 'BIKA: Add Doctor'
AddAetiologicAgent = 'BIKA: Add AetiologicAgent'
AddTreatment = 'BIKA: AddTreatment'
AddDrug = 'BIKA: Add Drug'
AddImmunization = 'BIKA: Add Immunization'
AddVaccinationCenter = 'BIKA: Add VaccinationCenter'
AddSymptom = 'BIKA: Add Symptom'
AddDrugProhibition = 'BIKA: Add DrugProhibition'

# Add Permissions for specific types, if required
ADD_CONTENT_PERMISSIONS = {
    'Doctor': AddDoctor,
    'Patient': AddPatient,
    'AetiologicAgent': AddAetiologicAgent,
    'Treatment': AddTreatment,
    'Drug': AddDrug,
    'Immunization': AddImmunization,
    'VaccinationCenter': AddVaccinationCenter,
    'Symptom': AddSymptom,
    'DrugProhibition': AddDrugProhibition,
}

ManageDoctors = "BIKA: Manage Doctors"
ManagePatients = "BIKA: Manage Patients"

ViewBatches = "BIKA: View Batches"
ViewSamples = "BIKA: View Samples"
ViewAnalysisRequests = "BIKA: View AnalysisRequests"
