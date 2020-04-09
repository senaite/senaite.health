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

from Products.CMFCore.utils import getToolByName
from Products.ZCTextIndex.ParseTree import ParseError
from bika.health.icd9cm import icd9_codes
from bika.lims.browser import BrowserView
from operator import itemgetter
import json
import plone


class ajaxGetSymptoms(BrowserView):
    """ Symptoms from ICD and Site Setup
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        title = 'title' in self.request and self.request['title'] or ''
        self.searchTerm = (len(title) == 0 and 'searchTerm' in self.request) and self.request['searchTerm'].lower() or title.lower()
        page = 'page' in self.request and self.request['page'] or 1
        nr_rows = 'rows' in self.request and self.request['rows'] or 10
        sord = 'sord' in self.request and self.request['sord'] or 'asc'
        sidx = 'sidx' in self.request and self.request['sidx'] or 'Title'
        rows = []

        # lookup objects from ZODB
        brains = self.bika_setup_catalog(portal_type='Symptom',
                                         is_active=True)
        if brains and self.searchTerm:
            for brain in brains:
                obj = brain.getObject()
                symptom = {'Code': obj.getCode(),
                           'Title': obj.Title(),
                           'Description': obj.Description()}
                rows.append(symptom)

        # lookup objects from ICD code list
        for icd9 in icd9_codes['R']:
            rows.append({'Code': icd9['code'],
                         'Title': icd9['short'],
                         'Description': icd9['long']})

        rows = self.filterBySearchCriteria(rows)
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

    def filterBySearchCriteria(self, rows):
        """
        Used to filter by code, title or description when you are typing the fields
        """
        return [r for r in rows if 
                r.get('Code','').lower().find(self.searchTerm) > -1 or
                r.get('Title','').lower().find(self.searchTerm) > -1 or
                r.get('Description','').lower().find(self.searchTerm) > -1]


class ajaxGetSymptomsByCode(ajaxGetSymptoms):

    def filterBySearchCriteria(self, rows):
        """
        Used to filter by code when you are typing on code field
        """
        return [r for r in rows if r.get('Code','').lower().find(self.searchTerm) > -1]


class ajaxGetSymptomsByTitle(ajaxGetSymptoms):

    def filterBySearchCriteria(self, rows):
        """
        Used to filter by title when you are typing on title field
        """
        return [r for r in rows if r.get('Title','').lower().find(self.searchTerm) > -1]


class ajaxGetSymptomsByDesc(ajaxGetSymptoms):

    def filterBySearchCriteria(self, rows):
        """
        Used to filter by description when you are typing on
        description field
        """
        return [r for r in rows if r.get('Description','').lower().find(self.searchTerm) > -1]
