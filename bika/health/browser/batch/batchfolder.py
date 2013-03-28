from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.lims.browser.batchfolder import BatchFolderContentsView as BaseView


class BatchFolderContentsView(BaseView):

    def __init__(self, context, request):
        super(BatchFolderContentsView, self).__init__(context, request)
        self.title = _("Cases")
        self.columns = {
            'BatchID': {'title': _('Case ID')},
            'Patient': {'title': _('Patient')},
            'Doctor': {'title': _('Doctor')},
            'Client': {'title': _('Client')},
            'state_title': {'title': _('State'), 'sortable': False},
        }
        self.review_states = [  # leave these titles and ids alone
            {'id':'default',
             'contentFilter': {'cancellation_state':'active',
                               'review_state': ['open', 'received', 'to_be_verified', 'verified']},
             'title': _('Open'),
             'columns':['BatchID',
                        'Patient',
                        'Doctor',
                        'Client',
                        'state_title', ]
             },
            {'id':'closed',
             'contentFilter': {'review_state': 'closed'},
             'title': _('Closed'),
             'columns':['BatchID',
                        'Patient',
                        'Doctor',
                        'Client',
                        'state_title', ]
             },
            {'id':'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled'},
             'columns':['BatchID',
                        'Patient',
                        'Doctor',
                        'Client',
                        'state_title', ]
             },
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns':['BatchID',
                        'Patient',
                        'Doctor',
                        'Client',
                        'state_title', ]
             },
        ]

    def folderitems(self):
        self.filter_indexes = None

        items = BaseView.folderitems(self)
        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']

            bid = obj.getBatchID()
            items[x]['BatchID'] = bid

            bpc = getToolByName(self.context, 'bika_patient_catalog')
            patient = bpc(portal_type='Patient', id=obj.getPatientID())
            client = self.portal_catalog(portal_type='Client', 
                                         getClientID=obj.getClientID())
            doctor = self.portal_catalog(portal_type='Doctor', 
                                         getDoctorID=obj.getDoctorID())

            items[x]['replace']['Patient'] = patient \
                and "<a href='%s'>%s</a>" % \
                (patient[0].getObject().absolute_url(),
                 patient[0].getObject().Title()) or ''

            items[x]['replace']['Doctor'] = doctor \
                and "<a href='%s'>%s</a>" % \
                (doctor[0].getObject().absolute_url(),
                 doctor[0].getObject().Title()) or ''

            items[x]['replace']['Client'] = client \
                and "<a href='%s'>%s</a>" % \
                (client[0].getObject().absolute_url(),
                 client[0].getObject().Title()) or ''

        return items