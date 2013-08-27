from bika.lims.browser.publish import doPublish
from bika.health import bikaMessageFactory as _h
from bika.lims import bikaMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AnalysisRequestPublish(doPublish):

    template = ViewPageTemplateFile("report_results.pt")

    def __call__(self):
        self.ar = self.analysis_requests[0]
        self.patient = self.ar.Schema()['Patient'].get(self.ar)
        return super(AnalysisRequestPublish, self).__call__()

    def get_mail_subject(self, ar):
        subject, totline = doPublish.get_mail_subject(self, ar)
        client = ar.aq_parent
        subject_items = client.getEmailSubject()
        if 'health.cp' in subject_items:
            pat = ar.Schema().getField('Patient').get(ar)
            cpid = pat and pat.getClientPatientID() or None
            if cpid:
                cps_line = _h('CPID: %s') % cpid
                if totline:
                    totline += ' '
                totline += cps_line

            subject = _('Analysis results for %s') % totline

        return subject, totline

    def get_formatted_lab_address(self):
        client_address = self.laboratory.getPostalAddress() \
            or self.laboratory.getBillingAddress() \
            or self.laboratory.getPhysicalAddress()
        addr = None
        if client_address:
            addr = self.get_formatted_address(client_address)
        return addr

    def get_formatted_client_address(self):
        client_address = self.client.getPostalAddress() \
            or self.contact.getBillingAddress() \
            or self.contact.getPhysicalAddress()
        addr = None
        if client_address:
            addr = self.get_formatted_address(client_address)
        return addr

    def get_formatted_address(self, address):
        addr = address.get('address')
        city = address.get('city')
        state = address.get('state')
        azip = address.get('zip')
        country = address.get('country')
        outaddress = None
        if addr:
            outaddress = addr

        strregion = None
        if azip and city and state and country:
            strregion = "%s %s (%s)<br/>%s" % (azip, city, state, country)
        elif azip and city and state:
            strregion = "%s %s<br/>%s" % (azip, city, state)
        elif azip and city and country:
            strregion = "%s %s<br/>%s" % (azip, city, country)
        elif azip and state and country:
            strregion = "%s %s<br/>%s" % (azip, state, country)
        elif azip and state:
            strregion = "%s %s" % (azip, state)
        elif azip and country:
            strregion = "%s %s" % (azip, country)
        elif azip:
            strregion = azip
        elif city and state and country:
            strregion = "%s (%s)<br/>%s" % (city, state, country)
        elif city and state:
            strregion = "%s<br/>%s" % (city, state)
        elif city and country:
            strregion = "%s<br/>%s" % (city, country)
        elif city:
            strregion = city
        elif country:
            strregion = country

        if addr and strregion:
            outaddress = "%s<br/>%s" % (addr, strregion)
        elif addr:
            outaddress = addr
        elif strregion:
            outaddress = strregion
        return outaddress
