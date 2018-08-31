# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json
from operator import itemgetter

import plone
from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.interfaces import ILabContact, IClient


class ajaxGetDoctors(BrowserView):
    """ vocabulary source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = 'searchTerm' in self.request and self.request['searchTerm'].lower() or ''
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        query = dict(portal_type="Doctor", inactive_state="active")
        client = self.get_current_client()
        if client:
            # Search those Doctors that are assigned to the same client or
            # that do not have any client assigned
            query["getPrimaryReferrerUID"] = [api.get_uid(client), None]

        doctors = api.search(query, 'portal_catalog')
        for doctor in doctors:
            doctor_id = doctor.id
            doctor_title = doctor.Title
            search_val = ('{} {}'.format(doctor_id, doctor_title)).lower()
            if searchTerm not in search_val:
                continue

            rows.append({'Title': doctor.Title() or '',
                         'DoctorID': doctor.getDoctorID(),
                         'DoctorSysID': doctor.id,
                         'DoctorUID': doctor.UID()})

        rows = sorted(rows, cmp=lambda x, y: cmp(x.lower(), y.lower()), key = itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'pages': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[(int(page) - 1) * int(nr_rows): int(page) * int(nr_rows)]}

        return json.dumps(ret)

    def get_current_client(self, default=None):
        """Returns the client the current user belongs to
        """
        user = api.get_current_user()
        roles = user.getRoles()
        if 'Client' not in roles:
            return default

        contact = api.get_user_contact(user)
        if not contact or ILabContact.providedBy(contact):
            return default

        client = api.get_parent(contact)
        if not client or not IClient.providedBy(client):
            return default

        return client
