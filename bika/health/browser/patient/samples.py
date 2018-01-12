# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser.sample import SamplesView as BaseView
from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as h


class SamplesView(BaseView):

    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)

        self.columns['Doctor'] = {'title': h('Doctor'), 'toggle': True}
        for rs in self.review_states:
            i = rs['columns'].index('getSampleID') + 1
            self.review_states[i]['columns'].insert(i, 'Doctor')

    def folderitems(self, full_objects = False):
        items = BaseView.folderitems(self, full_objects)
        wf = getToolByName(self.context, 'portal_workflow')
        outitems = []
        for x in range(len(items)):
            if 'obj' not in items[x]:
                items[x]['Doctor'] = ''
                continue
            sample = items[x]['obj']
            ars = sample.getAnalysisRequests()
            doctors = []
            doctorsanchors = []
            omit = False
            for ar in ars:
                patient = ar.Schema()['Patient'].get(ar)
                if not patient or patient.UID() != self.context.UID():
                    omit = True
                    continue
                doctor = ar.Schema()['Doctor'].get(ar) if ar else None
                if doctor and doctor.Title() not in doctors \
                    and wf.getInfoFor(ar, 'review_state') != 'invalid':
                    doctors.append(doctor.Title())
                    doctorsanchors.append("<a href='%s'>%s</a>" % (doctor.absolute_url(), doctor.Title()))
            if omit == False:
                items[x]['Doctor'] = ', '.join(doctors);
                items[x]['replace']['Doctor'] = ', '.join(doctorsanchors)
                outitems.append(items[x])
        return outitems
