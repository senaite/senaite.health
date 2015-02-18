from bika.health.browser.patients.folder_view import PatientsView
from bika.lims import bikaMessageFactory as _b
from Products.CMFCore.utils import getToolByName

""" This file contains overridden patient's functions to be used in insurance company's stuff.
"""


class PatientsView(PatientsView):

    def __init__(self, context, request):
        super(PatientsView, self).__init__(context, request)

    def _initFormParams(self):
        super(PatientsView, self)._initFormParams()
        if _b('Add') in self.context_actions:
            # We need to create the new element in the patients original url to avoid a creation error.
            self.context_actions[_b('Add')]['url'] = self.portal_url + '/patients/createObject?type_name=Patient'

    def folderitems(self):
        """ It filters patient's list by the current Insurance Company.
        :return: A dict with the results filtered by Insurance Comp.
        """
        items = super(PatientsView, self).folderitems()
        outitems = []
        companyuid = self.context.UID()
        for item in items:
            if 'obj' in item and item.get('obj'):
                pat = item.get('obj')
                if pat.getInsuranceCompany() and \
                   pat.getInsuranceCompany().UID() == companyuid:
                    outitems.append(item)
        return outitems
