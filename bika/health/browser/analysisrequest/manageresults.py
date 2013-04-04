from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.health.browser.analyses.view import AnalysesView
from bika.lims import logger
from bika.lims.browser.analysisrequest import \
    AnalysisRequestManageResultsView as BaseView


class ManageResultsView(BaseView):

    def __call__(self):

        super(ManageResultsView, self).__call__()

        # If there's analyses that exceed panic levels, show an alert message
        if self.hasAnalysesInPanic():
            message = self.context.translate(_('Some results exceeded the '
                                   'panic levels that may '
                                   'indicate an imminent '
                                   'life-threatening condition.'
                                   ))
            self.context.plone_utils.addPortalMessage(message, 'warning')
        return self.template()

    def hasAnalysesInPanic(self):
        bs = self.context.bika_setup
        if not hasattr(bs, 'getEnablePanicAlert') or bs.getEnablePanicAlert():
            wf = getToolByName(self.context, 'portal_workflow')
            for an in self.context.getAnalyses(full_objects=True):
                if an and wf.getInfoFor(an, 'review_state') != 'retracted':
                    try:
                        inpanic = an.isInPanicRange()
                        if inpanic and inpanic[0] == True:
                            return True
                    except:
                        logger.warning("Call error: isInPanicRange for "
                                       "analysis %s" % an.UID())
                        pass
        return False

    def createAnalysesView(self, context, request, **kwargs):
        return AnalysesView(context, request, **kwargs)
