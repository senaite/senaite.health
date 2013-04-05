from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.health import bikaMessageFactory as _
from bika.health.browser.analyses.view import AnalysesView
from bika.lims import logger
from bika.lims.browser.analysisrequest import AnalysisRequestViewView
from bika.lims.utils import encode_header
from email.Utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class AnalysisRequestView(AnalysisRequestViewView):

    def __call__(self):

        super(AnalysisRequestView, self).__call__()
        for row in self.header_rows:
            if row.get('id', '') == 'BatchID':
                row['title'] = _('Case ID')
                break

        autopopup = False
        bs = self.context.bika_setup
        sc = self.context
        try:
            autopopup = (hasattr(bs, 'getAutoShowPanicAlertEmailPopup') \
                        and bs.getAutoShowPanicAlertEmailPopup() \
                        and hasattr(sc, 'getPanicEmailAlertToClientSent') \
                        and not sc.Schema().getField('PanicEmailAlertToClientSent').get(sc)) \
                        or False
        except:
            autopopup = False
            pass

        if "email_popup_submit" in self.request:
            autopopup = False
            self.sendAlertEmail()

        # If there's analyses that exceed panic levels, show an alert message
        # with a link allowing the labmanager to send an email to client.
        # The link must only be shown if the current user is labmanager
        if self.hasAnalysesInPanic():
            self.addEmailLink(autopopup)

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

    def addEmailLink(self, autopopup=False):
        self.header_rows.append(
                {'id': 'Contact',
                 'title': "<a href='#' id='email_popup'>%s</a>" % \
                  (self.context.translate(_('Alert client about panic '
                                            'levels exceed'))),
                 'allow_edit': False,
                 'value': "<input name='email_popup_uid' autoshow='%s' "
                          "type='hidden' id='ar_uid' value='%s'/>" \
                           % (autopopup, self.context.UID()),
                 'condition': True,
                 'type': 'text'})

        message = self.context.translate(_('Some results exceeded the '
                                           'panic levels that may '
                                           'indicate an imminent '
                                           'life-threatening condition.'
                                           ))
        self.context.plone_utils.addPortalMessage(message, 'warning')

    def sendAlertEmail(self):
        # Send an alert email
        laboratory = self.context.bika_setup.laboratory
        subject = self.request.get('subject')
        to = self.request.get('to')
        body = self.request.get('body')
        mime_msg = MIMEMultipart('related')
        mime_msg['Subject'] = subject
        mime_msg['From'] = formataddr(
                    (encode_header(laboratory.getName()),
                     laboratory.getEmailAddress()))
        mime_msg['To'] = to
        msg_txt = MIMEText(safe_unicode(body).encode('utf-8'),
                           _subtype='html')
        mime_msg.preamble = 'This is a multi-part MIME message.'
        mime_msg.attach(msg_txt)
        succeed = False
        try:
            host = getToolByName(self.context, 'MailHost')
            host.send(mime_msg.as_string(), immediate=True)
            succeed = True
        except Exception, msg:
            ar = self.context.id
            logger.error("Panic level email %s: %s" % (ar, str(msg)))
            message = self.context.translate(
                    _('Unable to send an email to alert client '
                      'that some results exceeded the panic levels')
                                             + (": %s" % str(msg)))
            self.context.plone_utils.addPortalMessage(message, 'warning')

        if succeed:
            # Update AR (a panic alert email has been sent)
            ar = self.context
            try:
                ar.setPanicEmailAlertToClientSent(True)
                ar.reindexObject()
            except:
                pass
        return succeed

    def createAnalysesView(self, context, request, **kwargs):
        return AnalysesView(context, request, **kwargs)
