from bika.lims.browser import BrowserView
from bika.lims.permissions import *
import json
import plone


class ajax_rm_aetiologic(BrowserView):
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        nrs = []
        for nr in json.loads(self.request.get('nrs', "[]")):
            try:
                nrs.append(int(nr))
            except ValueError:
                continue
        if not nrs:
            return
        value = self.context.getAetiologicAgents()
        new = []
        for i, v in enumerate(value):
            if i in nrs:
                continue
            new.append(v)
        self.context.setAetiologicAgents(new)
