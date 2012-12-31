from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from bika.health.permissions import *
import json


class ajaxGetPatientLastReferralID(BrowserView):
    """ Returns the referral used on the last case from a patient
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        ret = {'clientid': '', 'clientname': ''}
        bpc = getToolByName(self, 'bika_catalog')
        batches = bpc(portal_type='Batch', getPatientID=self.context.id)
        if batches and batches[0]:
            batch = batches[0].getObject()
            clientid = batch.getClientID()
            if (clientid):
                ret['clientid'] = clientid
                pc = getToolByName(self, 'portal_catalog')
                clients = pc(portal_type='Client', UID=batch.getClientUID())
                if (clients and len(clients) > 0):
                    ret['clientname'] = clients[0].Title
        return json.dumps(ret)
