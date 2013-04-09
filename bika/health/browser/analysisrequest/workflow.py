from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.health import bikaMessageFactory as _
from bika.health.browser.calcs.calculateanalysisentry import \
    ajaxCalculateAnalysisEntry
from bika.lims import logger
from bika.lims.browser.analysisrequest import \
    AnalysisRequestWorkflowAction as BaseClass
from bika.lims.utils import encode_header
from bika.lims.utils import isActive
from email.Utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPRecipientsRefused
from smtplib import SMTPServerDisconnected
import App
from bika.lims import logger

class WorkflowAction(BaseClass):

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

                inpanic = [False, None, None]
                try:
                    inpanic = analysis.isInPanicRange()
                except:
                    logger.warning("Call error: isInPanicRange for analysis %s" % uid)
                    inpanic = [False, None, None]
                    pass

                if inpanic[0] == True:
                    inpanicanalyses.append(analysis)

            if len(inpanicanalyses) > 0:
                # Notify alerting of panic values
                message = self.context.translate(_('Some results exceeded the '
                                                   'panic levels that may '
                                                   'indicate an imminent '
                                                   'life-threatening condition'
                                                   ))
                self.context.plone_utils.addPortalMessage(message, 'warning')
                self.request.response.redirect(self.context.absolute_url())

                # If panic levels alert email enabled, send an email to 
                # labmanagers
                bs = self.context.bika_setup
                if hasattr(bs, 'getEnablePanicAlert') \
                    and bs.getEnablePanicAlert():
                    laboratory = self.context.bika_setup.laboratory
                    lab_address = "<br/>".join(laboratory.getPrintAddress())
                    managers = self.context.portal_groups.getGroupMembers('LabManagers')
                    mime_msg = MIMEMultipart('related')
                    mime_msg['Subject'] = _("Panic alert")
                    mime_msg['From'] = formataddr(
                        (encode_header(laboratory.getName()),
                         laboratory.getEmailAddress()))
                    to = []
                    for manager in managers:
                        user = self.portal.acl_users.getUser(manager)
                        uemail = user.getProperty('email')
                        ufull = user.getProperty('fullname')
                        to.append(formataddr((encode_header(ufull), uemail)))
                    mime_msg['To'] = ','.join(to)
                    strans = []
                    for an in inpanicanalyses:
                        serviceTitle = an.getServiceTitle()
                        result = an.getResult()
                        strans.append("- %s, result:%s" % (serviceTitle, result))
                    stran = "<br/>".join(strans)
                    text = _("Some results from the Analysis Request %s exceeded "
                             "the panic levels that may indicate an imminent "
                             "life-threatening condition:<br/><br/>"
                             "%s<br/><br/>"
                             "<b>Please, check the Analysis Request if you "
                             "want to re-test the analysis or immediately "
                             "alert the client.</b><br/><br/>%s"
                             ) % (inpanicanalyses[0].getRequestID(),
                                  stran,
                                  lab_address)

                    msg_txt = MIMEText(safe_unicode(text).encode('utf-8'),
                                       _subtype='html')
                    mime_msg.preamble = 'This is a multi-part MIME message.'
                    mime_msg.attach(msg_txt)
                    try:
                        host = getToolByName(self.context, 'MailHost')
                        host.send(mime_msg.as_string(), immediate=True)
                    except Exception, msg:
                        ar = inpanicanalyses[0].getRequestID()
                        logger.error("Panic level email %s: %s" % (ar, str(msg)))
                        message = self.context.translate(
                                _('Unable to send an email to alert lab '
                                  'managers that some analyses exceeded the '
                                  'panic levels') + (": %s" % str(msg)))
                        self.context.plone_utils.addPortalMessage(message, 'warning')
