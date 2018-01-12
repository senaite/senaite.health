# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.lims.browser.analysisrequest import AnalysisRequestWorkflowAction,\
    AnalysisRequestsView
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.lims.permissions import *
from bika.health.permissions import *
from bika.lims.subscribers import doActionFor, skip
from bika.lims.utils import isActive
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.i18n import translate
from zope.interface import implements
import json
import plone


class AnalysisRequestsView(AnalysisRequestsView):

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        # Filter by patient
        self.contentFilter['getPatientUID'] = self.context.UID()
        self.show_all = True
        self.columns['BatchID']['title'] = _('Case ID')

    def __call__(self):
        self.context_actions = {}
        wf = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        addPortalMessage = self.context.plone_utils.addPortalMessage
        PR = self.context.getPrimaryReferrer()
        if isActive(self.context):
            if mtool.checkPermission(AddAnalysisRequest, PR):
                #client contact required
                contacts = [c for c in PR.objectValues('Contact') if
                            wf.getInfoFor(c, 'inactive_state', '') == 'active']
                if contacts:
                    self.context_actions[self.context.translate(_('Add'))] = {
                        'url': PR.absolute_url() + "/ar_add",
                        'icon': '++resource++bika.lims.images/add.png'}
                else:
                    msg = _("Client contact required before request may be submitted")
                    addPortalMessage(self.context.translate(msg))

        return super(AnalysisRequestsView, self).__call__()
