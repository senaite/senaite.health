# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH.
#
# SENAITE.HEALTH is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _b
from bika.lims.browser import BrowserView


class BatchPublishView(BrowserView):
    """Publish a single Batch.
    """

    template = ViewPageTemplateFile("publish.pt")

    def __call__(self):

        pc = self.portal_catalog
        bc = self.bika_catalog
        bsc = self.bika_setup_catalog
        self.checkPermission = self.context.portal_membership.checkPermission
        self.now = DateTime()
        self.SamplingWorkflowEnabled = self.context.bika_setup.getSamplingWorkflowEnabled()

        # Client details (if client is associated)
        self.client = None
        client_uid = hasattr(self.context, 'getClientUID') and self.context.getClientUID()
        if client_uid:
            proxies = pc(portal_type='Client', UID=client_uid)
        if proxies:
            self.client = proxies[0].getObject()
            client_address = self.client.getPostalAddress() \
                or self.contact.getBillingAddress() \
                or self.contact.getPhysicalAddress()
            if client_address:
                _keys = ['address', 'city', 'state', 'zip', 'country']
                _list = [client_address.get(v) for v in _keys if client_address.get(v)]
                self.client_address = "<br/>".join(_list).replace("\n", "<br/>")
                if self.client_address.endswith("<br/>"):
                    self.client_address = self.client_address[:-5]
            else:
                self.client_address = None

        # Reporter
        self.member = self.context.portal_membership.getAuthenticatedMember()
        self.username = self.member.getUserName()
        self.reporter = self.user_fullname(self.username)
        self.reporter_email = self.user_email(self.username)
        self.reporter_signature = ""
        c = [x for x in self.bika_setup_catalog(portal_type='LabContact')
             if x.getObject().getUsername() == self.username]
        if c:
            sf = c[0].getObject().getSignature()
            if sf:
                self.reporter_signature = sf.absolute_url() + "/Signature"

        # laboratory
        self.laboratory = self.context.bika_setup.laboratory
        self.accredited = self.laboratory.getLaboratoryAccredited()
        lab_address = self.laboratory.getPrintAddress()
        if lab_address:
            _keys = ['address', 'city', 'state', 'zip', 'country']
            _list = [lab_address.get(v) for v in _keys if lab_address.get(v)]
            self.lab_address = "<br/>".join(_list).replace("\n", "<br/>")
            if self.lab_address.endswith("<br/>"):
                self.lab_address = self.lab_address[:-5]
        else:
            self.lab_address = None

        # Analysis Request results
        self.ars = []
        self.ar_headers = [_b("Request ID"),
                           _b("Date Requested"),
                           _b("Sample Type"),
                           _b("Sample Point")]
        self.analysis_headers = [_b("Analysis Service"),
                                 _b("Method"),
                                 _b("Result"),
                                 _b("Analyst")]
        for ar in self.context.getAnalysisRequests():
            datecreated = ar.created()
            datereceived = ar.getDateReceived()
            datepublished = ar.getDatePublished()
            datalines = []
            for analysis in ar.getAnalyses(full_objects=True):
                method = analysis.getMethod()
                sample = ar.getSample()
                result = analysis.getResult()
                try:
                    precision = analysis.getPrecision()
                    if not precision:
                        precision = "2"
                    result = float(result)
                    formatted_result = str("%." + precision + "f") % result
                except (TypeError, ValueError):
                    precision = "2"
                    formatted_result = result
                datalines.append({_b("Analysis Service"): analysis.Title(),
                                  _b("Method"): method and method.Title() or "",
                                  _b("Result"): formatted_result,
                                  _b("Analyst"): self.user_fullname(analysis.getAnalyst()),
                                  _b("Remarks"): analysis.getRemarks()})
            self.ars.append({
                _b("Request ID"): ar.getRequestID(),
                _b("Date Requested"): self.ulocalized_time(datecreated),  # requested->created
                _b("Sample Type"): sample.getSampleType() and sample.getSampleType().Title() or '',
                _b("Sample Point"): sample.getSamplePoint() and sample.getSamplePoint().Title() or '',
                _b("datalines"): datalines,
            })

        # Create Report
        fn = self.context.Title() + " " + self.ulocalized_time(self.now)
        report_html = self.template()

        debug_mode = App.config.getConfiguration().debug_mode
        if debug_mode:
            open(os.path.join(Globals.INSTANCE_HOME, 'var', fn + ".html"),
                 "w").write(report_html)

        pisa.showLogging()
        ramdisk = StringIO()
        pdf = pisa.CreatePDF(report_html, ramdisk)
        pdf_data = ramdisk.getvalue()
        ramdisk.close()

        if debug_mode:
            open(os.path.join(Globals.INSTANCE_HOME, 'var', fn + ".pdf"),
                 "wb").write(pdf_data)

        # Email to who?

        # Send PDF to browser
        if not pdf.err:
            setheader = self.request.RESPONSE.setHeader
            setheader('Content-Type', 'application/pdf')
            setheader("Content-Disposition", "attachment;filename=\"%s\"" % fn)
            self.request.RESPONSE.write(pdf_data)
