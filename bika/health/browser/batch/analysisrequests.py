from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.lims.browser.analysisrequest import AnalysisRequestsView
from bika.lims.browser.analysisrequest import AnalysisRequestAddView
from bika.lims.permissions import *
from bika.lims.utils import isActive
from zope.cachedescriptors.property import Lazy as lazy_property


class BatchAnalysisRequestsView(AnalysisRequestsView, AnalysisRequestAddView):

    template = ViewPageTemplateFile("analysisrequests.pt")

    def __init__(self, context, request):
        super(BatchAnalysisRequestsView, self).__init__(context, request)
        self.contentFilter['getBatchUID'] = self.context.UID()

    def __call__(self):
        self.context_actions = {}
        bc = getToolByName(self.context, 'bika_catalog')
        wf = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        addPortalMessage = self.context.plone_utils.addPortalMessage
        if isActive(self.context):
            if mtool.checkPermission(AddAnalysisRequest, self.portal):
                self.context_actions[self.context.translate(_('Add new'))] = {
                    'url': self.context.absolute_url() + '/ar_add?col_count=1',
                    'icon': '++resource++bika.lims.images/add.png'}
        return super(BatchAnalysisRequestsView, self).__call__()

    @lazy_property
    def Client(self):
        bc = getToolByName(self.context, 'bika_catalog')
        proxies = bc(portal_type="AnalysisRequest", getBatchUID=self.context.UID())
        if proxies:
            return proxies[0].getObject()

    def getMemberDiscountApplies(self):
        client = self.Client
        return client and client.getMemberDiscountApplies() or False

    def getRestrictedCategories(self):
        client = self.Client
        return client and client.getRestrictedCategories() or []

    def getDefaultCategories(self):
        client = self.Client
        return client and client.getDefaultCategories() or []
