from bika.lims.browser.sample import SamplesView as BaseView
from bika.health import bikaMessageFactory as _
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.bika_listing import BikaListingFilterBar\
    as BaseBikaListingFilterBar
from Products.Archetypes.public import DisplayList
import json
from datetime import datetime, date


class SamplesView(BaseView):
    """ Overrides bika.lims.browser.sample.SamplesView
        Shows additional columns with info about the Patient
    """

    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)

        # Add Patient fields
        self.columns['getPatientID'] = {'title': _('Patient ID'), 'toggle': True}
        self.columns['getClientPatientID'] = {'title': _("Client PID"), 'toggle': True}
        self.columns['getPatient'] = {'title': _('Patient'), 'toggle': True}
        self.columns['getDoctor'] = {'title': _('Doctor'), 'toggle': True}
        for rs in self.review_states:
            i = rs['columns'].index('getSampleID') + 1
            rs['columns'].insert(i, 'getClientPatientID')
            rs['columns'].insert(i, 'getPatientID')
            rs['columns'].insert(i, 'getPatient')
            rs['columns'].insert(i, 'getDoctor');

    def folderitems(self, full_objects=False):
        items = super(SamplesView, self).folderitems(full_objects)
        pm = getToolByName(self.context, "portal_membership")
        member = pm.getAuthenticatedMember()
        roles = member.getRoles()
        wf = getToolByName(self.context, 'portal_workflow')
        if 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles:
            # Remove patient fields. Must be done here because in __init__
            # method, member.getRoles() returns empty
            del self.columns['getPatientID']
            del self.columns['getClientPatientID']
            del self.columns['getPatient']
            del self.columns['getDoctor']
            for rs in self.review_states:
                del rs['columns'][rs['columns'].index('getClientPatientID')]
                del rs['columns'][rs['columns'].index('getPatientID')]
                del rs['columns'][rs['columns'].index('getPatient')]
                del rs['columns'][rs['columns'].index('getDoctor')]
        else:
            for x in range(len(items)):
                if 'obj' not in items[x]:
                    items[x]['getClientPatientID'] = ''
                    items[x]['getPatientID'] = ''
                    items[x]['getPatient'] = ''
                    items[x]['getDoctor'] = ''
                    continue
                patient = self.getPatient(items[x]['obj'])
                if patient:
                    items[x]['getPatientID'] = patient.getPatientID()
                    items[x]['replace']['getPatientID'] = "<a href='%s/analysisrequests'>%s</a>" % \
                        (patient.absolute_url(), items[x]['getPatientID'])
                    items[x]['getClientPatientID'] = patient.getClientPatientID()
                    items[x]['replace']['getClientPatientID'] = "<a href='%s/analysisrequests'>%s</a>" % \
                        (patient.absolute_url(), items[x]['getClientPatientID'])
                    items[x]['getPatient'] = patient.Title()
                    items[x]['replace']['getPatient'] = "<a href='%s/analysisrequests'>%s</a>" % \
                        (patient.absolute_url(), items[x]['getPatient'])
                else:
                    items[x]['getClientPatientID'] = ''
                    items[x]['getPatientID'] = ''
                    items[x]['getPatient'] = ''

                sample = items[x]['obj']
                ars = sample.getAnalysisRequests()
                doctors = []
                doctorsanchors = []
                for ar in ars:
                    doctor = ar.Schema()['Doctor'].get(ar) if ar else None
                    if doctor and doctor.Title() not in doctors \
                        and wf.getInfoFor(ar, 'review_state') != 'invalid':
                        doctors.append(doctor.Title())
                        doctorsanchors.append("<a href='%s'>%s</a>" % (doctor.absolute_url(), doctor.Title()))
                items[x]['getDoctor'] = ', '.join(doctors);
                items[x]['replace']['getDoctor'] = ', '.join(doctorsanchors)
        return items

    def getPatient(self, sample):
        # Onse sample can have more than one AR associated, but if is
        # the case, we must only take into account the one that is not
        # invalidated/retracted
        wf = getToolByName(self.context, 'portal_workflow')
        rawars = sample.getAnalysisRequests()
        ars = [ar for ar in rawars \
               if (wf.getInfoFor(ar, 'review_state') != 'invalid')]
        if (len(ars) == 0 and len(rawars) > 0):
            # All ars are invalid. Retrieve the info from the last one
            ar = rawars[len(rawars) - 1]
        elif (len(ars) > 1):
            # There's more than one valid AR
            # That couldn't happen never. Anyway, retrieve the last one
            ar = ars[len(ars) - 1]
        elif (len(ars) == 1):
            # One ar matches
            ar = ars[0]
        return ar.Schema()['Patient'].get(ar) if ar else None

    def isItemAllowed(self, obj):
        """
        Checks the BikaLIMS conditions and also checks filter bar conditions
        @Obj: it is a sample object.
        @return: boolean
        """
        return self.filter_bar_check_item(obj) and\
            super(SamplesView, self).isItemAllowed(obj)

    def getFilterBar(self):
        """
        This function creates an instance of BikaListingFilterBar if the
        class has not created one yet.
        :return: a BikaListingFilterBar instance
        """
        self._advfilterbar = self._advfilterbar if self._advfilterbar else \
            BikaListingFilterBar(context=self.context, request=self.request)
        return self._advfilterbar


class BikaListingFilterBar(BaseBikaListingFilterBar):
    """
    This class defines a filter bar to make advanced queries in
    BikaListingView. This filter shouldn't override the 'filter by state'
    functionality
    """

    def filter_bar_builder(self):
        """
        The template is going to call this method to create the filter bar in
        bika_listing_filter_bar.pt
        If the method returns None, the filter bar will not be shown.
        :return: a list of dictionaries as the filtering fields or None.
        """
        fields_dict = [{
            'name': 'sample_condition',
            'label': _('Sample condition'),
            'type': 'select',
            'voc': self._getSampleConditionsVoc(),
        }, {
            'name': 'sample_type',
            'label': _('Sample type'),
            'type': 'select',
            'voc': self._getSampleTypesVoc(),
        }, {
            'name': 'case',
            'label': _('Cases'),
            'type': 'autocomplete_text',
            'voc': json.dumps(self._getCasesVoc()),
        }, {
            'name': 'date_received',
            'label': _('Date received'),
            'type': 'date_range',
        },
        ]
        return fields_dict

    def _getSampleConditionsVoc(self):
        """
        Returns a DisplayList object with sample condtions.
        """
        l = self.context.bika_setup.bika_sampleconditions.listFolderContents()
        return DisplayList(
            [(element.UID(), element.Title()) for element in l])

    def _getSampleTypesVoc(self):
        """
        Returns a DisplayList object with sample types.
        """
        l = self.context.bika_setup.bika_sampletypes.listFolderContents()
        return DisplayList(
            [(element.UID(), element.Title()) for element in l])

    def _getCasesVoc(self):
        """
        Returns a list object with active cases ids.
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog({
            'portal_type': 'Batch',
            'review_state': 'open',
        })
        return [brain.id for brain in brains]

    def get_filter_bar_queryaddition(self):
        """
        This function gets the values from the filter bar inputs in order to
        create a query accordingly.
        Only returns the once that can be added to contentFilter dictionary.
        in this case, the catalog is bika_catalog
        In this case the keys with index representation are:
        - date_received - getDateReceived
        - date_received - BatchUID
        :return: a dictionary to be added to contentFilter.
        """
        query_dict = {}
        filter_dict = self.get_filter_bar_dict()
        # Date received filter
        if filter_dict.get('date_received_0', '') or\
                filter_dict.get('date_received_1', ''):
            date_0 = filter_dict.get('date_received_0') \
                if filter_dict.get('date_received_0', '')\
                else '1900-01-01'
            date_1 = filter_dict.get('date_received_1')\
                if filter_dict.get('date_received_1', '')\
                else datetime.strftime(date.today(), "%Y-%m-%d")
            date_range_query = {
                'query':
                (date_0 + ' 00:00', date_1 + ' 23:59'), 'range': 'min:max'}
            query_dict['getDateReceived'] = date_range_query
        # Batch(case) filter
        if filter_dict.get('case', ''):
            # removing the empty and space values and gettin their UIDs
            clean_list_ids = [
                a.strip() for a in filter_dict.get('case', '').split(',')
                if a.strip()]
            # Now we have the case(batch) ids, lets get their UIDs
            catalog = getToolByName(self, 'bika_catalog')
            brains = catalog(
                portal_type='Batch',
                cancellation_state='active',
                review_state='open',
                id=clean_list_ids
                )
            query_dict['BatchUID'] = [a.UID for a in brains]
        # Batch(case) filter
        if filter_dict.get('sample_type', ''):
            query_dict['getSampleTypeUID'] = filter_dict.get('sample_type', '')
        return query_dict

    def filter_bar_check_item(self, item):
        """
        This functions receives a key-value items, and checks if it should be
        displayed.
        It is recomended to be used in isItemAllowed() method.
        This function should be only used for those fields without
        representation as an index in the catalog.
        :item: The item to check.
        :return: boolean.
        """
        dbar = self.get_filter_bar_dict()
        keys = dbar.keys()
        final_decision = 'True'
        for key in keys:
            if key == 'sample_condition' and dbar.get(key, '') != '':
                if not item.getSampleCondition() or\
                        dbar.get(key, '') != item.getSampleCondition().UID():
                    return False
        return True
