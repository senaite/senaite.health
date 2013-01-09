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
        searchTerm = (len(title) == 0 and 'searchTerm' in self.request) and self.request['searchTerm'].lower() or title.lower()
        page = 'page' in self.request and self.request['page'] or 1
        nr_rows = 'rows' in self.request and self.request['rows'] or 10
        sord = 'sord' in self.request and self.request['sord'] or 'asc'
        sidx = 'sidx' in self.request and self.request['sidx'] or 'Title'
        rows = []

        # lookup objects from ZODB
        brains = self.bika_setup_catalog(portal_type='Symptom',
                                         inactive_state='active')
        if brains and searchTerm:
            brains = [p for p in brains if p.Title.lower().find(searchTerm) > -1
                      or p.Description.lower().find(searchTerm) > -1]
        for p in brains:
            p = p.getObject()
            if (len(title) > 0 and p.Title() == title):
                rows.append({'Code': p.getCode(),
                             'Title': p.Title(),
                             'Description': p.Description()})
            elif len(title) == 0:
                rows.append({'Code': p.getCode(),
                             'Title': p.Title(),
                             'Description': p.Description()})

        # lookup objects from ICD code list
        for icd9 in icd9_codes['R']:
            if icd9['code'].find(searchTerm) > -1 \
                or icd9['short'].lower().find(searchTerm) > -1 \
                    or icd9['long'].lower().find(searchTerm) > -1:

                if (len(title) > 0 and icd9['short'] == title):
                    rows.append({'Code': icd9['code'],
                                 'Title': icd9['short'],
                                 'Description': icd9['long']})
                elif len(title) == 0:
                    rows.append({'Code': icd9['code'],
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
