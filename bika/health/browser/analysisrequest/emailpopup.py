# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.health import bikaMessageFactory as _
from bika.health.browser.analysis.resultoutofrange import ResultOutOfRange
from bika.lims.browser import BrowserView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

import plone.protect


class EmailPopupView(BrowserView):
    implements(IViewView)

    template = ViewPageTemplateFile("emailpopup.pt")

    def __init__(self, context, request):
        super(EmailPopupView, self).__init__(context, request)
        path = "/++resource++bika.health.images"
        self.icon = self.portal_url + path + "/lifethreat_big.png"
        self.recipients = []
        self.ccs = ''
        self.subject = ''
        self.body = ''

    def __call__(self):
        workflow = getToolByName(self.context, 'portal_workflow')
        translate = self.context.translate
        plone.protect.CheckAuthenticator(self.request)
        bc = getToolByName(self.context, 'bika_catalog')
        ar = bc(UID=self.request.get('uid', None))

        if ar:
            ar = ar[0].getObject()
            self.ccs = []
            self.recipients = []

            contact = ar.getContact()
            if contact:
                email = contact.getEmailAddress()
                if email:
                    self.recipients = [{'uid': contact.UID(),
                                        'name': contact.Title(),
                                        'email': email}]
            for cc in ar.getCCContact():
                ccemail = cc.getEmailAddress()
                if ccemail:
                    self.ccs.append({'uid': cc.UID(),
                                     'name': cc.Title(),
                                     'email': ccemail})
            analyses = ar.getAnalyses()
            strans = []
            for analysis in analyses:
                analysis = analysis.getObject()
                astate = workflow.getInfoFor(analysis, 'review_state')
                if astate == 'retracted':
                    continue
                panic_alerts = ResultOutOfRange(analysis)()
                if panic_alerts:
                    result = analysis.getResult()
                    strans.append("- {0}, {1}: {2}".format(
                        analysis.Title(), translate(_("Result")), result))
            stran = "\n".join(strans)

            laboratory = self.context.bika_setup.laboratory
            lab_address = "\n".join(laboratory.getPrintAddress())

            self.body = translate(
                _("Some results from the Analysis Request ${ar} "
                  "exceeded the panic levels that may indicate an "
                  "imminent life-threatening condition: \n\n${arlist}\n"
                  "\n\n${lab_address}",
                  mapping={'ar': ar.getRequestID(),
                           'arlist': stran,
                           'lab_address': lab_address})
            )
            self.subject = translate(
                _("Some results from ${ar} exceeded panic range",
                  mapping={'ar': ar.getRequestID()})
            )

        return self.template()

    def getFormattedRecipients(self):
        outrecip = []
        for recipient in self.recipients:
            name = recipient['name']
            email = recipient['email']
            outrecip.append("%s <%s>" % (name, email))
        return ', '.join(outrecip)
