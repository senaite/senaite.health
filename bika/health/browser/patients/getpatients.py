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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
from operator import itemgetter

import plone
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView


class ajaxGetPatients(BrowserView):
    """ Patient vocabulary source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = 'searchTerm' in self.request and self.request['searchTerm'].lower() or ''
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        clientid = 'clientuid' in self.request and self.request['clientuid'] or ''

        rows = []

        # lookup patient objects from ZODB
        # AdvancedQuery is faster, but requires whole words.
        # if searchTerm and len(searchTerm) < 3:
        #     return json.dumps(rows)
        # We'll have to do something else to make this acceptable.
        # aq = MatchRegexp('Title', "%s" % searchTerm) | \
        #      MatchRegexp('Description', "%s" % searchTerm) | \
        #      MatchRegexp('getPatientID', "%s" % searchTerm)
        # brains = bikahealth_catalog_patient_listing.evalAdvancedQuery(aq)

        bpc = getToolByName(self.context, 'bikahealth_catalog_patient_listing')
        proxies = bpc(portal_type='Patient', is_active=True)
        for patient in proxies:
            addidfound = False
            addids = patient.getPatientIdentifiersStr

            if addids.lower().find(searchTerm) > -1:
                addidfound = True
                break

            if patient.Title.lower().find(searchTerm) > -1 \
                or patient.getPatientID.lower().find(searchTerm) > -1 \
                or addidfound:
                if clientid == '' or clientid == patient.getPrimaryReferrerUID:
                    rows.append({'Title': patient.Title or '',
                                 'PatientID': patient.getPatientID,
                                 'ClientPatientID': patient.getClientPatientID,
                                 'ClientTitle': patient.getPrimaryReferrerTitle,
                                 'PatientUID': patient.UID,
                                 'AdditionalIdentifiers': patient.getPatientIdentifiersStr,
                                 'PatientBirthDate': self.ulocalized_time(patient.getBirthDate, long_format=0),
                                 'PatientGender': patient.getGender,
                                 })

        rows = sorted(rows, cmp=lambda x, y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[(int(page) - 1) * int(nr_rows): int(page) * int(nr_rows)]}

        return json.dumps(ret)
