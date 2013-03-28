from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import logger
from bika.health import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import plone.protect


class EmailPopupView(BrowserView):
    implements(IViewView)

    template = ViewPageTemplateFile("emailpopup.pt")

    def __init__(self, context, request):
        super(EmailPopupView, self).__init__(context, request)
        self.icon = self.portal_url + "/++resource++bika.health.images/lifethreat_big.png"
        self.recipients = []
        self.ccs = ''
        self.subject = ''
        self.body = ''

    def __call__(self):
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

            inpanicanalyses = []
            workflow = getToolByName(ar, 'portal_workflow')
            analyses = ar.getAnalyses()
            for analysis in analyses:
                analysis = analysis.getObject()
                if workflow.getInfoFor(analysis, 'review_state') == 'retracted':
                    continue

                inpanic = [False, None, None]
                try:
                    inpanic = analysis.isInPanicRange()
                except:
                    logger.warning("Call error: isInPanicRange for analysis %s" % analysis.UID())
                    pass

                if inpanic[0] == True:
                    inpanicanalyses.append(analysis)

            laboratory = self.context.bika_setup.laboratory
            lab_address = "<br/>".join(laboratory.getPrintAddress())
            strans = []
            for an in inpanicanalyses:
                serviceTitle = an.getServiceTitle()
                result = an.getResult()
                strans.append("- %s, result:%s" % (serviceTitle, result))
            stran = "<br/>".join(strans)
            self.body = _("Some results from the Analysis Request %s exceed "
                         "the panic levels that may indicate an inmminent "
                         "life-threatening condition<br/>: %s<br/>"
                         "<br/><br/>%s"
                         ) % (ar.getRequestID(),
                              stran,
                              lab_address)

            self.subject = _("Some results from %s exceed panic range") % ar.id

        return self.template()

    def getFormattedRecipients(self):
        outrecip = []
        for recipient in self.recipients:
            name = recipient['name']
            email = recipient['email']
            outrecip.append("%s <%s>" %(name, email))
        return ', '.join(outrecip)
