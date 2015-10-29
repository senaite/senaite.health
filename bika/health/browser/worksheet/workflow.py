from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.health import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser.worksheet.workflow import \
    WorksheetWorkflowAction as BaseClass
from bika.lims.utils import encode_header
from bika.lims.utils import isActive
from email.Utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import App
from bika.health.browser.analysis.resultoutofrange import ResultOutOfRange


class WorkflowAction(BaseClass):

    def __call__(self):
        # Do generic bika.lims stuff
        BaseClass.__call__(self)
        # Do bika-health specific actions when submit
        action = BaseClass._get_form_workflow_action(self)
        addPortalMessage = self.context.plone_utils.addPortalMessage
        if action[0] == 'submit' and isActive(self.context):
            inpanicanalyses = []
            workflow = getToolByName(self.context, 'portal_workflow')
            translate = self.context.translate
            rc = getToolByName(self.context, REFERENCE_CATALOG)
            uc = getToolByName(self.context, 'uid_catalog')
            # retrieve the results from database and check if
            # the values are exceeding panic levels
            alerts = {}
            for uid in self.request.form['Result'][0].keys():
                analysis = rc.lookupObject(uid)
                analysis = analysis.getObject() if hasattr(analysis, 'getObject') else analysis
                if not analysis:
                    continue
                astate = workflow.getInfoFor(analysis, 'review_state')
                if astate == 'retracted':
                    continue
                alerts.update(ResultOutOfRange(analysis)())
            if alerts:
                message = translate(_('Some results exceeded the '
                                      'panic levels that may '
                                      'indicate an imminent '
                                      'life-threatening condition'
                                      ))
                addPortalMessage(message, 'warning')
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
                    for analysis_uid, alertlist in alerts:
                        analysis = uc(analysis_uid).getObject()
                        for alert in alertlist:
                            strans.append("- {0}, {1}: {2}".format(
                                          analysis.getService().Title(),
                                          translate(_("Result")),
                                          analysis.getResult()))
                    stran = "<br/>".join(strans)
                    text = translate(_(
                        "Some results from ${items} exceeded the panic levels "
                        "that may indicate an imminent life-threatening "
                        "condition: <br/><br/>{analysisresults}<br/><br/>"
                        "<b>Please, check the Analysis Request if you "
                        "want to re-test the analysis or immediately "
                        "alert the client.</b><br/><br/>{lab_address}",
                        mapping={'items': self.context.getId(),
                                 'analysisresults': stran,
                                 'lab_address': lab_address}))
                    msg_txt = MIMEText(safe_unicode(text).encode('utf-8'),
                                       _subtype='html')
                    mime_msg.preamble = 'This is a multi-part MIME message.'
                    mime_msg.attach(msg_txt)
                    try:
                        host = getToolByName(self.context, 'MailHost')
                        host.send(mime_msg.as_string(), immediate=True)
                    except Exception as msg:
                        ar = inpanicanalyses[0].getRequestID()
                        logger.error(
                            "Panic level email %s: %s" % (ar, str(msg)))
                        message = self.context.translate(
                            _('Unable to send an email to alert lab '
                              'managers that some analyses exceeded the '
                              'panic levels') + (": %s" % str(msg)))
                        self.context.plone_utils.addPortalMessage(
                            message, 'warning')
