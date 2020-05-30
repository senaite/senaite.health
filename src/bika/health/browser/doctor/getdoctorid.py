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
