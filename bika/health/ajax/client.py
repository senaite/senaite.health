# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.health.ajax.ajaxhandler import AjaxHandler


class ClientAjaxHandler(AjaxHandler):

    def getPublicationSettings(self, params):
        """ Returns the settings for the publication of results to patients.
            The first output param is a dictionary with the following
            key/values:
            - AllowResultsDistributionToPatients: true/false
            - PatientPublicationPreferences: array of strings (email, etc.)
            - PatientPublicationAttachmentsPermitted: true/false
            If client not found, first param values are those from the default
            BikaSetup settings.
            The first output param is Null if there was an error.
            The second output param is an error message if there was an error
            invoking the method. Null if there was no error.
        """
        uid = params.get('uid', '')
        if not uid:
            error = _("Parameter '%s' is missing") % 'uid'
            return None, error

        DEF = 'DefaultResultsDistributionToPatients'
        ALLOW = 'AllowResultsDistributionToPatients'
        PREF = 'PatientPublicationPreferences'
        ATTACH = 'PatientPublicationAttachmentsPermitted'
        res = {}

        bc = getToolByName(self.context, 'portal_catalog')
        proxies = bc(UID=uid)

        defsettings = True
        if len(proxies) == 1:
            client = proxies[0].getObject()
            sch = client.Schema()
            defsettings = sch[DEF].get(client)
            if defsettings == False:
                res = {ALLOW: sch[ALLOW].get(client),
                       PREF: sch[PREF].get(client),
                       ATTACH: sch[ATTACH].get(client)}
        if defsettings:
            # Retrieve from Bika Setup
            bs = self.context.bika_setup
            sch = bs.Schema()
            res = {ALLOW: sch[ALLOW].get(bs),
                   PREF: sch[PREF].get(bs),
                   ATTACH: sch[ATTACH].get(bs)}

        return res, None
