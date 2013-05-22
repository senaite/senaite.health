from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.lims.browser.client import ClientBatchesView


class BatchesView(ClientBatchesView):

    def __init__(self, context, request):
        super(BatchesView, self).__init__(context, request)
        self.title = _("Cases")
        self.columns = {
            'BatchID': {'title': _('Case ID')},
            'getClientPatientID': {'title': _('Client PID')},
            'Patient': {'title': _('Patient'),
                        'index': 'getPatientTitle'},
            'Doctor': {'title': _('Doctor'),
                        'index': 'getDoctorTitle'},
            'Client': {'title': _('Client'),
                        'index': 'getClientTitle'},
            'OnsetDate': {'title': _('Onset Date')},
            'state_title': {'title': _('State'), 'sortable': False},
        }
        self.review_states = [  # leave these titles and ids alone
            {'id':'default',
             'contentFilter': {'cancellation_state':'active',
                               'review_state': ['open', 'sample_received',
                                                'to_be_verified', 'verified'],
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'title': _('Open'),
             'columns':['BatchID',
                        'getClientPatientID',
                        'Patient',
                        'Doctor',
                        'Client',
                        'OnsetDate',
                        'state_title', ]
             },
            {'id':'closed',
             'contentFilter': {'review_state': 'closed',
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'title': _('Closed'),
             'columns':['BatchID',
                        'getClientPatientID',
                        'Patient',
                        'Doctor',
                        'Client',
                        'OnsetDate',
                        'state_title', ]
             },
            {'id':'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled',
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'columns':['BatchID',
                        'getClientPatientID',
                        'Patient',
                        'Doctor',
                        'Client',
                        'OnsetDate',
                        'state_title', ]
             },
            {'id':'all',
             'title': _('All'),
             'contentFilter':{'sort_on':'created',
                              'sort_order': 'reverse'},
             'columns':['BatchID',
                        'getClientPatientID',
                        'Patient',
                        'Doctor',
                        'Client',
                        'OnsetDate',
                        'state_title', ]
             },
        ]

    def contentsMethod(self, contentFilter):
        batches = {}
        bc = getToolByName(self.context, "bika_catalog")
        for batch in bc(portal_type='Batch',
                        getClientUID = self.context.UID()):
            batch = batch.getObject()
            batches[batch.UID()] = batch 
        return batches.values()

    def folderitems(self):
        self.filter_indexes = None

        items = ClientBatchesView.folderitems(self)
        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']

            bid = obj.getBatchID()
            items[x]['BatchID'] = bid

            patient = obj.Schema()['Patient'].get(obj)
            client = obj.Schema()['Client'].get(obj)
            doctor = obj.Schema()['Doctor'].get(obj)

            if 'Doctor' not in items[x]:
                items[x]['Doctor'] = ''

            if 'Patient' not in items[x]:
                items[x]['Patient'] = ''

            if 'Client' not in items[x]:
                items[x]['Client'] = ''

            if 'OnsetDate' not in items[x]:
                items[x]['OnsetDate'] = ''

            items[x]['replace']['Patient'] = patient \
                and "<a href='%s'>%s</a>" % \
                (patient.absolute_url(),
                 patient.Title()) or ''

            items[x]['replace']['Doctor'] = doctor \
                and "<a href='%s'>%s</a>" % \
                (doctor.absolute_url(),
                 doctor.Title()) or ''

            items[x]['replace']['Client'] = client \
                and "<a href='%s'>%s</a>" % \
                (client.absolute_url(),
                 client.Title()) or ''

            onsetdate = obj.Schema()['OnsetDate'].get(obj)
            items[x]['replace']['OnsetDate'] = onsetdate \
                and self.ulocalized_time(onsetdate) or ''

            items[x]['getClientPatientID'] = patient \
                            and patient.getClientPatientID() \
                            or ''
            items[x]['replace']['getClientPatientID'] = patient \
                            and "<a href='%s'>%s</a>" % \
                                (patient.absolute_url(), 
                                 items[x]['getClientPatientID']) \
                            or ''

        return items
