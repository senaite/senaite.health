from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.lims import bikaMessageFactory as _b
from bika.lims.browser import BrowserView
from bika.lims.permissions import *
import json
import plone

class ajaxGetBatchInfo(BrowserView):
    """ Grab the details for Doctor, Patient, Hospital (Titles).
    These are displayed onload next to the ID fields, but they are not part of the schema.
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)

        bpc = getToolByName(self.context, 'bika_patient_catalog')
        batch = self.context

        client = batch.Schema()['Client'].get(batch)
        doctor = batch.Schema()['Doctor'].get(batch)
        patient = batch.Schema()['Patient'].get(batch)

        patientids = ''
        if patient:
            value = patient.getPatientIdentifiersStr()
            patientids = len(value) > 0 and "("+value+")" or ''

        ret = {'ClientID': client and client.getClientID() or '',
               'ClientUID': client and client.UID() or '',
               'ClientTitle': client and client.Title() or '',
               'PatientID': patient and patient.getPatientID() or '',
               'PatientUID': patient and patient.UID() or '',
               'PatientTitle': patient and patient.Title() or '',
               'DoctorID': doctor and doctor.getDoctorID(),
               'DoctorUID': doctor and doctor.UID() or '',
               'DoctorTitle': doctor and doctor.Title() or ''}

        return json.dumps(ret)

