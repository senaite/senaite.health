from bika.lims.browser.publish import doPublish
from bika.health import bikaMessageFactory as _h
from bika.lims import bikaMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AnalysisRequestPublish(doPublish):

    template = ViewPageTemplateFile("report_results.pt")

    def __call__(self):
        return super(AnalysisRequestPublish, self).__call__()

    def get_patient(self, ar):
        return ar.Schema().getField('Patient').get(ar) \
            if 'Patient' in ar.Schema() else None

    def get_mail_subject(self, ar):
        subject, totline = doPublish.get_mail_subject(self, ar)
        client = ar.aq_parent
        subject_items = client.getEmailSubject()
        if 'health.cp' in subject_items:
            pat = self.get_patient(ar)
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

    def get_recipients(self, ar):
        recips = super(AnalysisRequestPublish, self).get_recipients(ar)

        bs = self.context.bika_setup
        sch = bs.Schema()
        bs_allowdist = sch['AllowResultsDistributionToPatients'].get(bs)
        bs_pubprefs = sch['PatientPublicationPreferences'].get(bs)

        # Add Patient recipients
        pat = self.get_patient(ar)
        if pat:
            sch = pat.Schema()
            email_field = pat.getField('EmailAddress')
            pa_allowdist_field = pat.getField('AllowResultsDistribution')
            inherit_field = pat.getField('DefaultResultsDistribution')
            email = email_field.get(pat) if email_field else None
            pa_allowdist = pa_allowdist_field.get(pat) if pa_allowdist_field else False
            inherit = inherit_field.get(pat) if inherit_field else True
            if inherit == True:
                # Gets the results distribution from the client
                client = ar.aq_parent
                inherit_field = client.getField('DefaultResultsDistributionToPatients')
                cl_allowdist_field = client.getField('AllowResultsDistributionToPatients')
                cl_allowdist = cl_allowdist_field.get(client) if cl_allowdist_field else False
                inherit = inherit_field.get(client) if inherit_field else True

                if inherit == True and bs_allowdist == True:
                    # Gets the results distribution from BikaSetup
                    recips.append({'title':pat.Title(),
                                   'email':email,
                                   'pubpref':bs_pubprefs})

                elif inherit == False and cl_allowdist == True:
                    # Gets the results distribution from Client
                    cl_pubpref_field = client.getField('PatientPublicationPreferences')
                    cl_pubpref = cl_pubpref_field.get(client) if cl_pubpref_field else []
                    recips.append({'title':pat.Title(),
                                   'email':email,
                                   'pubpref':cl_pubpref})

            elif pa_allowdist == True:
                # Gets the pub preferences from the patient
                pub_field = pat.getField('PublicationPreferences')
                pubpref = pub_field.get(pat) if pub_field else []
                recips.append({'title':pat.Title(),
                               'email':email,
                               'pubpref':pubpref})

        return recips
