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
        patientids = ''
        client = self.portal_catalog(portal_type='Client',
                                     getClientID=batch.getClientID())
        if client:
            client = client[0].getObject()
        patient = bpc(portal_type='Patient',
                      id=batch.getPatientID())
        if patient:
            patient = patient[0].getObject()
            patientids = len(patient.getPatientIdentifiersStr()) > 0 and "("+patient.getPatientIdentifiersStr()+")" or ''
        doctor = self.portal_catalog(portal_type='Doctor',
                                     getDoctorID=batch.getDoctorID())
        if doctor:
            doctor = doctor[0].getObject()

        ret = {'Client': client and "<a class='edit_client' href='%s/base_edit'>%s</a>"%(client.absolute_url(), client.Title()) or '',
               'Patient': patient and "<a class='edit_patient' href='%s/edit'>%s</a> %s"%(patient.absolute_url(), patient.Title(), patientids) or '',
               'Doctor': doctor and "<a class='edit_doctor' href='%s/edit'>%s</a>"%(doctor.absolute_url(), doctor.Title()) or '',
               'ClientID': batch.getClientID(),
               'PatientID': batch.getPatientID(),
               'DoctorID': batch.getDoctorID(),
               'ClientUID': client and client.UID() or '',
               'PatientUID': patient and batch.UID() or '',
               'DoctorUID': patient and patient.UID() or '',
               'ClientTitle': client and client.Title() or '',
               'PatientTitle': patient and patient.Title() or '',
               'DoctorTitle': doctor and doctor.Title() or '',
               }

        return json.dumps(ret)

