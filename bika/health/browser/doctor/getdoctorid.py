# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser import BrowserView
from Products.ZCTextIndex.ParseTree import ParseError
from bika.health.permissions import *
import json
import plone


class ajaxGetDoctorID(BrowserView):
    """ Grab ID for newly created doctor (#420)
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        Fullname = self.request.get('Fullname', '')
        if not Fullname:
            return json.dumps({'DoctorID': ''})
        proxies = None
        try:
            proxies = self.portal_catalog(portal_type='Doctor', Title=Fullname, sort_on='created', sort_order='reverse')
        except ParseError:
            pass
        if not proxies:
            return json.dumps({'DoctorID': ''})
        return json.dumps({'DoctorID': proxies[0].getObject().getDoctorID(),
                           'DoctorSysID': proxies[0].getObject().id})
