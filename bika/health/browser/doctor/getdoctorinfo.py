# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.ZCTextIndex.ParseTree import ParseError
from bika.lims.browser import BrowserView
from Products.CMFCore.utils import getToolByName
import plone
import json


class ajaxGetDoctorInfo(BrowserView):
    """ Grab details of newly created doctor
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        Fullname = self.request.get('Fullname', '')
        uid = self.request.get('UID', '')
        ret = {'id': '',
               'DoctorID': '',
               'UID': '',
               'Fullname': ''}

        bpc = getToolByName(self.context, 'portal_catalog')
        proxies = None
        if uid:
            try:
                proxies = bpc(UID=uid)
            except ParseError:
                pass
        elif Fullname:
            try:
                proxies = bpc(Title=Fullname,
                              sort_on='created',
                              sort_order='reverse')
            except ParseError:
                pass

        if not proxies:
            return json.dumps(ret)

        doctor = proxies[0].getObject()
        ret = {'DoctorID': doctor.getDoctorID(),
               'id': doctor.id,
               'UID': doctor.UID(),
               'Fullname': doctor.Title()}
        return json.dumps(ret)
