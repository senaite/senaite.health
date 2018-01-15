# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.health import bikaMessageFactory as _
from bika.lims import bikaMessageFactory as _b
from bika.lims import PMF as _p
from bika.lims.browser import BrowserView
from bika.lims.permissions import *


class ImmunizationHistoryView(BrowserView):
    template = ViewPageTemplateFile("immunizationhistory.pt")

    def __call__(self):
        if 'submitted' in self.request:
            self.context.setImmunizationHistory(self.request.form.get('ImmunizationHistory', ()))
            self.context.plone_utils.addPortalMessage(_p("Changes saved"))
        return self.template()
