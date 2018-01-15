# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
