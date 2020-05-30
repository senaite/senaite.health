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
from bika.lims.browser.widgets import RecordsWidget
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.idserver import renameAfterCreation
from bika.health.permissions import *
from operator import itemgetter
import json
import plone

class CaseAetiologicAgentsWidget(RecordsWidget):
    _properties = RecordsWidget._properties.copy()
    _properties.update({
        'helper_js': ("bika_health_widgets/caseaetiologicagentswidget.js",),
    })

registerWidget(CaseAetiologicAgentsWidget,
               title='Aetiologic agents',
               description="Laboratory confirmed aetiologic agent and subtype, as the disease's cause",
               )
