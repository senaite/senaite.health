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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import StringWidget
from Products.CMFCore.permissions import View
from zope.component import getMultiAdapter

class ReadonlyStringWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro' : "bika_health_widgets/readonlystringwidget",
        'css' : "readonly",
        })
    security = ClassSecurityInfo()

    security.declareProtected(View, 'readonly')
    def readonly(self, context, request):
        portal_state = getMultiAdapter((context, request), name="plone_portal_state")
        if portal_state.anonymous():
            return None
        else:
            return '1'

registerWidget(ReadonlyStringWidget,
               title='ReadonlyString',
               description=('HTML input text in readonly mode'),
               )
