# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH.
#
# SENAITE.HEALTH is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

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
