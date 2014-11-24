from bika.lims.browser.analysisrequest.publish import \
    AnalysisRequestPublishView as _AnalysisRequestPublishView
from bika.health import bikaMessageFactory as _h
from bika.lims import bikaMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import glob, os, sys, traceback

class AnalysisRequestPublishView(_AnalysisRequestPublishView):

    def __call__(self):
        return super(AnalysisRequestPublishView, self).__call__()

    def getAvailableFormats(self):
        """ Overrides
            Looks for templates inside bika.health's templates/reports
            folder, as well as bika.lims's templates/reports directory
        """
        # bika.lims templates
        btempl = _AnalysisRequestPublishView.getAvailableFormats(self)
        for tmpl in btempl:
            tmpl['title'] = '%s: %s' % ('bika.lims', tmpl['title']);
            tmpl['id'] = '%s:%s' % ('bika.lims', tmpl['id']);

        # bika.health templates
        tempath = self._getTemplatesResourcePath('*.pt')
        templates = [t.split('/')[-1] for t in glob.glob(tempath)]
        out = []
        for template in templates:
            out.append({
                'id': '%s:%s' % ('bika.health', template),
                'title': '%s: %s' % ('bika.health', template[:-3])})

        out.extend(btempl)
        return out

    def getReportTemplate(self):
        """ Overrides
            Returns the template for the current ar and moves to the
            next ar to be processed. Uses the selected template
            specified in the request ('template' parameter)
        """
        embedt = self.request.get('template', self._DEFAULT_TEMPLATE)
        path = self._getTemplatesResourcePath(embedt)
        embed = ViewPageTemplateFile(path)
        reptemplate = ""
        try:
            reptemplate = embed(self)
        except:
            tbex = traceback.format_exc()
            arid = self._ars[self._current_ar_index].id
            reptemplate = "<div class='error-report'>%s - %s '%s':<pre>%s</pre></div>" % (arid, _("Unable to load the template"), embedt, tbex)
            self.logger.error(tbex);
        self._nextAnalysisRequest()
        return reptemplate

    def getReportStyle(self):
        """ Overrides
            Returns the CSS to be used in the current template
        """
        embedt = self.request.get('template', self._DEFAULT_TEMPLATE)
        path = "%s.css" % self._getTemplatesResourcePath(embedt)[:-3]
        content = ''
        with open(path, 'r') as content_file:
            content = content_file.read()
        return content

    def _getTemplatesResourcePath(self, resource):
        """ Returns the full path from any resource located inside
            /templates/reports, either from inside bika.lims project
            or bika.health project
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        res = resource
        if 'bika.lims:' in resource:
            this_dir = str.replace(this_dir, "bika.health/bika/health", "bika.lims/bika/lims")
            res = str.replace(resource, 'bika.lims:', '')
        res = str.replace(res, 'bika.health:', '')
        path = os.path.join(this_dir, 'templates/reports')
        path = '%s/%s' % (path, res)
        return path

    def get_patient(self, ar):
        return ar.Schema().getField('Patient').get(ar) \
            if 'Patient' in ar.Schema() else None

    def get_doctor(self, ar):
        return ar.Schema().getField('Doctor').get(ar) \
            if 'Doctor' in ar.Schema() else None

    def get_mail_subject(self, ar):
        subject, totline = super(AnalysisRequestPublishView, self).get_mail_subject(ar)
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
        lab = self.context.bika_setup.laboratory
        client_address = lab.getPostalAddress() \
            or lab.getBillingAddress() \
            or lab.getPhysicalAddress()
        addr = None
        if client_address:
            addr = self.get_formatted_address(client_address)
        return addr

    def get_formatted_client_address(self, ar):
        client = ar.getClient()
        contact = ar.getContact();
        client_address = client.getPostalAddress() \
            or contact.getBillingAddress() \
            or contact.getPhysicalAddress()
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
        recips = super(AnalysisRequestPublishView, self).get_recipients(ar)

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

        # Add Doctor recipient
        doctor = self.get_doctor(ar)
        if doctor:
            email_field = doctor.getField('EmailAddress')
            email = email_field.get(doctor) if email_field else None
            pubpref = doctor.getField('PublicationPreference')
            pubpref = pubpref.get(doctor) if pubpref else []
            recips.append({'title': doctor.Title(),
                           'email': email,
                           'pubpref': pubpref})

        return recips

    def get_historicresults(self, patient):
        from bika.health.browser.patient.historicresults import get_historicresults as historic
        dates, data = historic(patient)
        return {'dates': dates,
                'results': data}

    def sortDictTitles(self, analyses_dict):
        sorted_t_list = list()
        sorted_list = list()
        for analysis in analyses_dict:
            sorted_t_list.append((analyses_dict[analysis]['title'],analysis))
        sorted_t_list.sort()
        for tanalysis,nanalysis in sorted_t_list:
            sorted_list.append(nanalysis)
        return sorted_list
