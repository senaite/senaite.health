# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from bika.lims.browser.senaitefrontpage import FrontPageView as BaseView


class FrontPageView(BaseView):
    """SENAITE Health default Front Page
    """
    template = ViewPageTemplateFile("senaite-frontpage.pt")
