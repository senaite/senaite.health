# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import PMF as _p
from bika.lims.browser import BrowserView


class ChronicConditionsView(BrowserView):
    template = ViewPageTemplateFile("chronicconditions.pt")

    def __call__(self):
        if 'submitted' in self.request:
            self.context.setChronicConditions(self.request.form.get('ChronicConditions', ()))
            self.context.plone_utils.addPortalMessage(_p("Changes saved"))
        return self.template()
