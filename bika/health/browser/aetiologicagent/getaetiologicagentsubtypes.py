# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser import BrowserView
from bika.lims.permissions import *
from operator import itemgetter
import json
import plone


class ajaxGetAetiologicAgentSubtypes(BrowserView):
    """ Aetologic Agent Subtypes for a specified Aetiologic Agent from site setup
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        title = 'title' in self.request and self.request['title'] or ''
        auid = 'auid' in self.request and self.request['auid'] or ''
        searchTerm = (len(title) == 0 and 'searchTerm' in self.request) and self.request['searchTerm'].lower() or title.lower()
        page = 'page' in self.request and self.request['page'] or 1
        nr_rows = 'rows' in self.request and self.request['rows'] or 10
        sord = 'sord' in self.request and self.request['sord'] or 'asc'
        sidx = 'sidx' in self.request and self.request['sidx'] or 'Subtype'
        rows = []

        agents = self.bika_setup_catalog(portal_type='AetiologicAgent', UID=auid)
        if agents and len(agents) == 1:
            agent = agents[0].getObject()
            subtypes = agent.getAetiologicAgentSubtypes()
            if subtypes and searchTerm:
                subtypes = [subtype for subtype in subtypes if subtype['Subtype'].lower().find(searchTerm) > -1]

        for subtype in subtypes:
            if (len(title) > 0 and subtype['Subtype'] == title):
                rows.append({'Subtype': subtype['Subtype'],
                             'SubtypeRemarks': subtype.get('SubtypeRemarks', '')})
            elif len(title) == 0:
                rows.append({'Subtype': subtype['Subtype'],
                             'SubtypeRemarks': subtype.get('SubtypeRemarks', '')})

        rows = sorted(rows, cmp=lambda x, y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'Subtype'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[(int(page) - 1) * int(nr_rows): int(page) * int(nr_rows)]}

        return json.dumps(ret)
