# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.lims.browser.sample import SampleEdit as BaseClass


class SampleEditView(BaseClass):
    """ Overrides bika.lims.browser.sample.SampleEdit
        Shows additional information to be edited about the Patient
    """

    def __call__(self):
        super(SampleEditView, self).__call__()

        # Add Patient fields
        pm = getToolByName(self.context, "portal_membership")
        member = pm.getAuthenticatedMember()
        roles = member.getRoles()

        # TODO: Needs to be changed by creating a new permission and set it
        #       into profiles/default/workflow_csv
        if 'Manager' in roles or 'LabManager' in roles or 'LabClerk' in roles:
            if self.context.portal_type == 'AnalysisRequest':
                ar = self.context
            else:
                # Onse sample can have more than one AR associated, but if is
                # the case, we must only take into account the one that is not
                # invalidated/retracted
                wf = getToolByName(self.context, 'portal_workflow')
                rawars = self.context.getAnalysisRequests()
                ars = [ar for ar in rawars \
                       if (wf.getInfoFor(ar, 'review_state') != 'invalid')]
                if (len(ars) == 0 and len(rawars) > 0):
                    # All ars are invalid. Retrieve the info from the last one
                    ar = rawars[len(rawars) - 1]
                elif (len(ars) > 1):
                    # There's more than one valid AR
                    # That couldn't happen never. Anyway, retrieve the last one
                    ar = ars[len(ars) - 1]
                elif (len(ars) == 1):
                    # One ar matches
                    ar = ars[0]

#            patient = ar.Schema()['Patient'].get(ar) if ar else None
#            if patient:
#                self.header_rows.append(
#                {'id': 'Patient',
#                 'title': _('Patient'),
#                 'allow_edit': False,
#                 'value': "<a href='%s'>%s</a>" % (patient.absolute_url(),
#                                                   patient.Title()),
#                 'condition': True,
#                 'type': 'text'})
#
#                self.header_rows.append(
#                {'id': 'PatientID',
#                 'title': _('Patient ID'),
#                 'allow_edit': False,
#                 'value': "<a href='%s'>%s</a>" % (patient.absolute_url(),
#                                                   patient.getPatientID() 
#                                                   or ''),
#                 'condition':True,
#                 'type': 'text'})
#
#                self.header_rows.append(
#                {'id': 'ClientPatientID',
#                 'title': _('Client Patient ID'),
#                 'allow_edit': False,
#                 'value': "<a href='%s'>%s</a>" % (patient.absolute_url(),
#                                                   patient.getClientPatientID() 
#                                                   or ''),
#                 'condition':True,
#                 'type': 'text'})
                
        return self.template()

