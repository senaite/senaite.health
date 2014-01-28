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
                        'url': PR.absolute_url() + "/portal_factory/"
                        "AnalysisRequest/Request new analyses/ar_add",
                        'icon': '++resource++bika.lims.images/add.png'}
                else:
                    msg = _("Client contact required before request may be submitted")
                    addPortalMessage(self.context.translate(msg))

        return super(AnalysisRequestsView, self).__call__()

    def folderitems(self, full_objects=False):
        #HACK pending to solve by using getPatientUID directly in __init__
        #https://github.com/bikalabs/Bika-LIMS/issues/678
        outitems = []
        items = super(AnalysisRequestsView, self).folderitems(full_objects)
        patientuid = self.context.UID()
        for item in items:
            try:
                if 'obj' in item \
                    and item.get('obj'):
                    ar = item.get('obj')
                    if ar.Schema().getField('Patient').get(ar).UID() == patientuid:
                        outitems.append(item)
            except:
                pass
        return outitems
