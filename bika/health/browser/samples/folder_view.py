# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser.sample import SamplesView as BaseView
from bika.health import bikaMessageFactory as _
from Products.CMFCore.utils import getToolByName


class SamplesView(BaseView):
    """ Overrides bika.lims.browser.sample.SamplesView
        Shows additional columns with info about the Patient
    """

    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)

        # Add Patient fields
        self.columns['getPatientID'] = {
            'title': _('Patient ID'),
            'sortable': False,
            'toggle': True}
        self.columns['getClientPatientID'] = {
            'title': _("Client PID"),
            'sortable': False,
            'toggle': True}
        self.columns['getPatient'] = {
            'title': _('Patient'),
            'sortable': False,
            'toggle': True}
        self.columns['getDoctor'] = {
            'title': _('Doctor'),
            'sortable': False,
            'toggle': True}
        for rs in self.review_states:
            i = rs['columns'].index('getSampleID') + 1
            rs['columns'].insert(i, 'getClientPatientID')
            rs['columns'].insert(i, 'getPatientID')
            rs['columns'].insert(i, 'getPatient')
            rs['columns'].insert(i, 'getDoctor')

    def folderitems(self, full_objects=False):
        items = super(SamplesView, self).folderitems(full_objects)
        pm = getToolByName(self.context, "portal_membership")
        member = pm.getAuthenticatedMember()
        roles = member.getRoles()
        wf = getToolByName(self.context, 'portal_workflow')
        if 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles:
            # Remove patient fields. Must be done here because in __init__
            # method, member.getRoles() returns empty
            del self.columns['getPatientID']
            del self.columns['getClientPatientID']
            del self.columns['getPatient']
            del self.columns['getDoctor']
            for rs in self.review_states:
                del rs['columns'][rs['columns'].index('getClientPatientID')]
                del rs['columns'][rs['columns'].index('getPatientID')]
                del rs['columns'][rs['columns'].index('getPatient')]
                del rs['columns'][rs['columns'].index('getDoctor')]
        else:
            for x in range(len(items)):
                if 'obj' not in items[x]:
                    items[x]['getClientPatientID'] = ''
                    items[x]['getPatientID'] = ''
                    items[x]['getPatient'] = ''
                    items[x]['getDoctor'] = ''
                    continue
                sample = items[x]['obj']
                patient = sample.getField('Patient').get(sample)
                if patient:
                    items[x]['getPatientID'] = patient.getPatientID()
                    items[x]['replace']['getPatientID'] = "<a href='%s/analysisrequests'>%s</a>" % \
                        (patient.absolute_url(), items[x]['getPatientID'])
                    items[x]['getClientPatientID'] = patient.getClientPatientID()
                    items[x]['replace']['getClientPatientID'] = "<a href='%s/analysisrequests'>%s</a>" % \
                        (patient.absolute_url(), items[x]['getClientPatientID'])
                    items[x]['getPatient'] = patient.Title()
                    items[x]['replace']['getPatient'] = "<a href='%s/analysisrequests'>%s</a>" % \
                        (patient.absolute_url(), items[x]['getPatient'])
                else:
                    items[x]['getClientPatientID'] = ''
                    items[x]['getPatientID'] = ''
                    items[x]['getPatient'] = ''

                ars = sample.getAnalysisRequests()
                doctors = []
                doctorsanchors = []
                for ar in ars:
                    doctor = ar.Schema()['Doctor'].get(ar) if ar else None
                    if doctor and doctor.Title() not in doctors \
                        and wf.getInfoFor(ar, 'review_state') != 'invalid':
                        doctors.append(doctor.Title())
                        doctorsanchors.append("<a href='%s'>%s</a>" % (doctor.absolute_url(), doctor.Title()))
                items[x]['getDoctor'] = ', '.join(doctors);
                items[x]['replace']['getDoctor'] = ', '.join(doctorsanchors)
        return items
