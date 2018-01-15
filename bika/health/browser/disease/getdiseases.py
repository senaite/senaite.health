# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

"""Fetch diseases from ICD and bika_setup tables
"""
from bika.health import bikaMessageFactory as _
from bika.lims import bikaMessageFactory as _b
from bika.lims.browser import BrowserView
from bika.lims.permissions import *
from operator import itemgetter
from bika.health.icd9cm import icd9_codes
import json
import plone


class ajaxGetDiseases(BrowserView):
    """ Diseases from ICD
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = 'searchTerm' in self.request and self.request['searchTerm'].lower() or ''
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        # lookup objects from ZODB
        brains = self.bika_setup_catalog(portal_type='Disease',
                                         inactive_state='active')
        if brains and searchTerm:
            brains = [p for p in brains if p.Title.lower().find(searchTerm) > -1
                      or p.Description.lower().find(searchTerm) > -1]
        for p in brains:
            p = p.getObject()
            rows.append({'Code': p.getICDCode(),
                         'Title': p.Title(),
                         'Description': p.Description()})

        for icdprefix in icd9_codes.keys():
            for icd9 in icd9_codes[icdprefix]:
                if (str(icdprefix) + str(icd9['code'])).lower().find(searchTerm) > -1 \
                    or icd9['short'].lower().find(searchTerm) > -1 \
                        or icd9['long'].lower().find(searchTerm) > -1:
                    rows.append({'Code': str(icdprefix) + str(icd9['code']),
                                 'Title': icd9['short'],
                                 'Description': icd9['long']})

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
