from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser.worksheet import ManageResultsView as BaseView


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
