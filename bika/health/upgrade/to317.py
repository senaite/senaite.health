from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.utils import tmpID
from bika.lims.idserver import renameAfterCreation
from bika.health.permissions import AddEthnicity, ViewEthnicities
from bika.lims import logger


def upgrade(tool):

    # Adding bika.health.analysisrequest.ar_add_health_standard.js
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    typestool = getToolByName(portal, 'portal_types')

    # Since this new version changes the hard-coded ethnicity to a new content type ethnicity, we need to save all
    # patients' ethnicities to create and load them later. Otherwise, all patient with an ethnicity defined will lost
    # its ethnicity value.

    # Getting all patients brains
    bpc = getToolByName(tool, 'bika_patient_catalog')
    all_patients = bpc(portal_type='Patient')
    # Initializing the list that will contain tuples with the actual (patientUID,ethnicity)
    patient_list = []
    for patient in all_patients:
        # Obtaining patient object
        patient_obj = patient.getObject()
        # Obtaining patient's ethnicity name and uid
        pa_ethnicity = patient_obj.Schema()['Ethnicity'].get(patient_obj)
        pa_uid = patient_obj.UID()
        if pa_ethnicity != '':
            # If the patient contains an ethnicity, it should be saved in the list
            patient_list.append((pa_uid, pa_ethnicity))
    # reread jsregistry with the new data
    setup.runImportStepFromProfile('profile-bika.health:default', 'jsregistry')
    # Reread cssregistry to update the changes
    setup.runImportStepFromProfile('profile-bika.health:default', 'cssregistry')
    # Reread typeinfo to update/add the modified/added types
    setup.runImportStepFromProfile('profile-bika.health:default', 'typeinfo')
    # Reread factorytool to add the the new ethnicity type
    setup.runImportStepFromProfile('profile-bika.health:default', 'factorytool')
    # Reread workflow to add the the new ethnicity type
    setup.runImportStepFromProfile('profile-bika.health:default', 'workflow')
    # Reread controlpanel to add the the new ethnicity type
    setup.runImportStepFromProfile('profile-bika.health:default', 'controlpanel')

    # Adding Ethnicity roles
    workflow = getToolByName(portal, 'portal_workflow')
    workflow.updateRoleMappings()

    # Adding Ethnicity content type
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('Ethnicity', ['bika_setup_catalog', ])
    # If the type is not created yet, we should create it
    if not portal['bika_setup'].get('bika_ethnicities'):
        typestool.constructContent(type_name="Ethnicities",
                                   container=portal['bika_setup'],
                                   id='bika_ethnicities',
                                   title='Ethnicity')
    obj = portal['bika_setup']['bika_ethnicities']
    obj.unmarkCreationFlag()
    obj.reindexObject()
    if not portal['bika_setup'].get('bika_ethnicities'):
        logger.info("Ethnicities not created")

    # Define permissions for ethnicity
    mp = portal.manage_permission
    mp(AddEthnicity, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(ViewEthnicities, ['Manager', 'LabManager', 'Owner', 'LabClerk', 'Doctor', 'RegulatoryInspector'], 1)

    # Creating all standard ethnicities
    createEthnicities(tool)
    # Relating new ethnicity contents types with patients
    addPatientEthnicity(tool, patient_list)

    return True


def createEthnicities(context):
    """
    This function creates al the standard ethnicities
    :return: a list of tuples with the created ethnicities contents as: [(ethnicity_name, ethnicity_uid), (), ...]
    """
    ethnicities = ['Native American', 'Asian', 'Black', 'Native Hawaiian or Other Pacific Islander', 'White',
                   'Hispanic or Latino']
    for ethnicityname in ethnicities:
        folder = context.bika_setup.bika_ethnicities
        # Generating a temporal object
        _id = folder.invokeFactory('Ethnicity', id=tmpID())
        obj = folder[_id]
        # Setting its values
        obj.edit(title=ethnicityname,
                 description='')
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)


def addPatientEthnicity(context, patient_list):
    """
    This function adds to the patient, its ethnicity.
    :Patient_list: is a list of tuples. Each tuple contains a patient UID and a string. This string is the name of the
    ethnicity that used te be related in the patient.  [(patientUID, ethnicityName),(),...]
    :return: Ethnicity object
    """
    for patientUID,ethnicityname in patient_list:
        # Getting the ethnicity uid
        bsc = getToolByName(context, 'bika_setup_catalog')
        bpc = getToolByName(context, 'bika_patient_catalog')
        if len(bsc(Portal_type='Ethnicity', Title=ethnicityname)[0].getObject().UID()) == 1:
            ethnicityUID = bsc(Portal_type='Ethnicity', Title=ethnicityname)[0].getObject().UID()
            # Getting the patient object
            patient = bpc(Portal_type='Patient', UID=patientUID)[0].getObject()
            patient.setEthnicity(ethnicityUID)
