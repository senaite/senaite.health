# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
