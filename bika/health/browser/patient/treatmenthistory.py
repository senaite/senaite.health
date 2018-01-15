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


class TreatmentHistoryView(BrowserView):
    template = ViewPageTemplateFile("treatmenthistory.pt")

    def __call__(self):
        if 'submitted' in self.request:
            self.context.setTreatmentHistory(self.request.form.get('TreatmentHistory', ()))
            self.context.plone_utils.addPortalMessage(_p("Changes saved"))
        return self.template()
