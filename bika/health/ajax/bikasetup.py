# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.health.ajax.ajaxhandler import AjaxHandler


class BikaSetupAjaxHandler(AjaxHandler):

    def getDefaultPatientPublicationSettings(self, params):
        """ Returns the settings for the publication of results to patients.
            The first output param is a dictionary with the following
            key/values:
            - AllowResultsDistributionToPatients: true/false
            - PatientPublicationPreferences: array of strings (email, etc.)
            - PatientPublicationAttachmentsPermitted: true/false
            The first output param is Null if there was an error.
            The second output param is an error message if there was an error
            invoking the method. Null if there was no error.
        """
        ALLOW = 'AllowResultsDistributionToPatients'
        PREF = 'PatientPublicationPreferences'
        ATTACH = 'PatientPublicationAttachmentsPermitted'

        bs = self.context.bika_setup
        sch = bs.Schema()
        res = {ALLOW: sch[ALLOW].get(bs),
                PREF: sch[PREF].get(bs),
                ATTACH: sch[ATTACH].get(bs)}

        return res, None
