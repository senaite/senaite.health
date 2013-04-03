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
        #self.contentFilter['getPatientUID'] = self.context.UID()
        self.columns['BatchID']['title'] = _('Case ID')

    def __call__(self):
        self.context_actions = {}
        wf = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        addPortalMessage = self.context.plone_utils.addPortalMessage
        PR = self.context.getPrimaryReferrer()
        if isActive(self.context):
            if mtool.checkPermission(AddAnalysisRequest, PR):
                self.context_actions[self.context.translate(_('Add'))] = {
                    'url': self.context.absolute_url() + '/ar_add',
                    'icon': '++resource++bika.lims.images/add.png'}
        return super(AnalysisRequestsView, self).__call__()

    def folderitems(self, full_objects=False):
        #HACK pending to solve by using getPatientUID directly in __init__
        #https://github.com/bikalabs/Bika-LIMS/issues/678
        bc = getToolByName(self.context, 'bika_catalog')
        buids = [b.UID for b in bc(portal_type='Batch',
                                   getPatientID=self.context.id)]
        outitems = []
        items = super(AnalysisRequestsView, self).folderitems(full_objects)
        for item in items:
            if item.get('obj').getBatchUID() in buids:
                outitems.append(item)
        return outitems
