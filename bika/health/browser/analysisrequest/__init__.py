from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.health import bikaMessageFactory as _
from bika.health.browser.calcs.calculateanalysisentry import \
    ajaxCalculateAnalysisEntry
from bika.lims.browser.analysisrequest import \
    AnalysisRequestWorkflowAction as BaseClass
from bika.lims.utils import isActive
from bika.lims.utils import sendmail, encode_header
from cStringIO import StringIO
from email import Encoders
from email.MIMEBase import MIMEBase
from email.Utils import formataddr
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import join
from smtplib import SMTPRecipientsRefused
from smtplib import SMTPServerDisconnected
import App
from Products.CMFCore.WorkflowCore import WorkflowException


class AnalysisRequestWorkflowAction(BaseClass):

    def __call__(self):
        # Do generic bika.lims stuff
        BaseClass.__call__(self)

        # Do bika-health specific actions when submit
        action = BaseClass._get_form_workflow_action(self)
        if action[0] == 'submit' and isActive(self.context):
            inpanicanalyses = []
            workflow = getToolByName(self.context, 'portal_workflow')
            rc = getToolByName(self.context, REFERENCE_CATALOG)

            # retrieve the results from database and check if
            # the values are exceeding panic levels
            for uid in self.request.form['Result'][0].keys():

                # lookup from database
                analysis = rc.lookupObject(uid)
                if not analysis or \
                    workflow.getInfoFor(analysis, 'review_state') == 'retracted':
                    continue

                aresult = analysis.getResult()
                calcs = ajaxCalculateAnalysisEntry(self.context, self.request)
                inpanic = calcs.result_in_panic(analysis, aresult, 'lab')
                if inpanic[0] == True:
                    inpanicanalyses.append(analysis)

            if len(inpanicanalyses) > 0:
                # Notify alerting of panic values
                message = self.context.translate(_('Some results exceed the '
                                                   'panic levels that may '
                                                   'indicate an inminent '
                                                   'life-threatening condition'
                                                   ))
                self.context.plone_utils.addPortalMessage(message, 'warning')
                self.request.response.redirect(self.context.absolute_url())

                # If panic levels alert email enabled, send an email to 
                # labmanagers
                bs = self.context.bika_setup
                if not hasattr(bs, 'getEnablePanicAlert') \
                    or bs.getEnablePanicAlert():
                    laboratory = self.context.bika_setup.laboratory
                    lab_address = "<br/>".join(laboratory.getPrintAddress())
                    managers = analysis.aq_parent.getManagers()
                    mime_msg = MIMEMultipart('related')
                    mime_msg['Subject'] = _("Panic alert")
                    mime_msg['From'] = formataddr(
                        (encode_header(laboratory.getName()),
                         laboratory.getEmailAddress()))
                    to = []
                    for manager in managers:
                        to.append(formataddr((encode_header(manager.getFullname()),
                                             manager.getEmailAddress())))
                    mime_msg['To'] = ','.join(to)
                    strans = []
                    for an in inpanicanalyses:
                        serviceTitle = an.getServiceTitle()
                        result = an.getResult()
                        strans.append("- %s, result:%s" % (serviceTitle, result))
                    stran = "<br/>".join(strans)
                    text = _("Some results from the Analysis Request %s exceed "
                             "the panic levels that may indicate an inmminent "
                             "life-threatening condition<br/>: "
                             ""
                             "%s<br/>"
                             ""
                             "<b>Please, check the Analysis Request if the "
                             "you want to retest the analysis or immediately "
                             "alert the client.</b><br/><br/>%s"
                             ) % (inpanicanalyses[0].getRequestID(),
                                  stran,
                                  lab_address)

                    msg_txt = MIMEText(safe_unicode(text).encode('utf-8'),
                                       _subtype='html')
                    mime_msg.attach(msg_txt)
                    debug_mode = App.config.getConfiguration().debug_mode
                    try:
                        host = getToolByName(self.context, 'MailHost')
                        host.send(mime_msg.as_string(), immediate=True)
                    except SMTPServerDisconnected, msg:
                        if not debug_mode:
                            raise SMTPServerDisconnected(msg)
                    except SMTPRecipientsRefused, msg:
                        raise WorkflowException(str(msg))
