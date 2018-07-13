# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json

import plone
from Products.CMFCore.utils import getToolByName
from bika.health.ajax.ajaxhandler import AjaxHandler
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IClient


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


class ajaxGetClientInfoFromCurrentUser(BrowserView):
    """Returns the client information associated to the current user (if the
    current user has a contact associated that it's parent is a Client).
    Otherwise, returns an empty dict
    """

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        curr_user = api.get_current_user()
        contact = api.get_user_contact(curr_user, contact_types=['Contact'])
        parent = contact and contact.getParent() or None
        if parent and not IClient.providedBy(parent):
            parent = None
        ret = {'ClientTitle': parent and parent.Title() or '',
               'ClientID': parent and parent.getClientID() or '',
               'ClientSysID': parent and parent.id or '',
               'ClientUID': parent and parent.UID() or '',}
        return json.dumps(ret)
