# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.health import bikaMessageFactory as _
from bika.health.browser.analysis.resultoutofrange import ResultOutOfRange
from bika.health import logger
from bika.lims.browser.analysisrequest import AnalysisRequestViewView
from bika.lims.utils import encode_header
from email.Utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class AnalysisRequestView(AnalysisRequestViewView):

    def __call__(self):

        result = super(AnalysisRequestView, self).__call__()

        if "email_popup_submit" in self.request:
            self.sendAlertEmail()

        if self.hasAnalysesInPanic():
            message = _('Some results exceeded the panic levels that may '
                        'indicate an imminent life-threatening condition.')
            self.addMessage(message, 'warning')
        if result is None:
            return
        self.renderMessages()
        return self.template()

    def isPanicAlertAutopopupEnabled(self):
        if "email_popup_submit" in self.request:
            return False

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
        return autopopup

    def get_custom_fields(self):
        custom = super(AnalysisRequestView, self).get_custom_fields()
        # If there's analyses that exceed panic levels, show an alert message
        # with a link allowing the labmanager to send an email to client.
        # The link must only be shown if the current user is labmanager
        autopopup = self.isPanicAlertAutopopupEnabled()
        if self.hasAnalysesInPanic():
            msg = _('Alert client about panic levels exceeded')
            custom['Contact']={'title': "<a href='#' id='email_popup'>%s</a>" \
                                        % self.context.translate(msg),
                               'value': "<input name='email_popup_uid' autoshow='%s' "
                                        "type='hidden' id='ar_uid' value='%s'/>" \
                                        % (autopopup, self.context.UID())}
        return custom

    def hasAnalysesInPanic(self):
        workflow = getToolByName(self.context, 'portal_workflow')
        items = self.context.getAnalyses()
        alerts = {}
        for obj in items:
            obj = obj.getObject() if hasattr(obj, 'getObject') else obj
            astate = workflow.getInfoFor(obj, 'review_state')
            if astate == 'retracted':
                continue
            alerts.update(ResultOutOfRange(obj)())
        return alerts

    def sendAlertEmail(self):
        # Send an alert email
        laboratory = self.context.bika_setup.laboratory
        subject = self.request.get('subject')
        to = self.request.get('to')
        body = self.request.get('body')
        body = "<br/>".join(body.split("\r\n"))
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
        except Exception, msg:
            ar = self.context.id
            logger.error("Panic level email %s: %s" % (ar, str(msg)))
            message = _('Unable to send an email to alert client '
                        'that some results exceeded the panic levels') \
                                             + (": %s" % str(msg))
            self.addMessage(message, 'warning')
        else:
            # Update AR (a panic alert email has been sent)
            ar = self.context
            try:
                ar.setPanicEmailAlertToClientSent(True)
                ar.reindexObject()
            except:
                pass
        return succeed
