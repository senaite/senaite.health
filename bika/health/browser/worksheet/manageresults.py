# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.health.browser.analysis.resultoutofrange import ResultOutOfRange
from bika.lims.browser.worksheet.views import \
    ManageResultsView as BaseView


class ManageResultsView(BaseView):

    def __call__(self):
        workflow = getToolByName(self.context, 'portal_workflow')
        # If there's analyses that exceed panic levels, show an alert message
        analyses = self._getAnalyses()
        for obj in analyses:
            obj = obj.getObject() if hasattr(obj, 'getObject') else obj
            astate = workflow.getInfoFor(obj, 'review_state')
            if astate == 'retracted':
                continue
            panic_alerts = ResultOutOfRange(obj)()
            if panic_alerts:
                translate = self.context.translate
                addPortalMessage = self.context.plone_utils.addPortalMessage
                message = translate(
                    _('Some results exceeded the '
                      'panic levels that may '
                      'indicate an imminent '
                      'life-threatening condition.'))
                addPortalMessage(message, 'warning')
                break

        return super(ManageResultsView, self).__call__()
