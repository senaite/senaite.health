# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.health.browser.sample.edit import SampleEditView


class SampleView(SampleEditView):
    """ Overrides bika.lims.browser.sample.SampleView (through SampleEdit)
        Shows additional information inside the table_header about the Patient
        if exists in the attached Analysis Request
    """

    def __call__(self):
        self.allow_edit = False
        return super(SampleView, self).__call__()
