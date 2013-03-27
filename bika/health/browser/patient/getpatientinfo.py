from Products.ZCTextIndex.ParseTree import ParseError
from bika.lims.browser import BrowserView
from Products.CMFCore.utils import getToolByName
import plone
import json


class ajaxGetPatientInfo(BrowserView):
    """ Grab details of newly created patient (#420)
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        Fullname = self.request.get('Fullname', '')
        ret = {'PatientID': '',
               'ClientID': '',
               'ClientTitle': '',
               'PatientFullname': Fullname,
               'PatientBirthDate': '',
               'PatientGender':'dk'}
        if not Fullname:
            return json.dumps(ret)
        proxies = None
        try:
            bpc = getToolByName(self.context, 'bika_patient_catalog')
            proxies = bpc(Title=Fullname,
                          sort_on='created',
                          sort_order='reverse')
        except ParseError:
            pass
        if not proxies:
            return json.dumps(ret)
        patient = proxies[0].getObject()
        PR = patient.getPrimaryReferrer()
        ret = {'PatientID': patient.getPatientID(),
               'ClientID': PR and PR.getClientID() or '',
               'ClientTitle': PR and PR.Title() or '',
               'ClientSysID' : PR and PR.id or '',
               'PatientFullname': Fullname,
               'PatientBirthDate': self.ulocalized_time(patient.getBirthDate()),
               'PatientGender': patient.getGender()}
        return json.dumps(ret)
