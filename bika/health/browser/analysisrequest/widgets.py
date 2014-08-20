from bika.lims.browser.analysisrequest import WidgetVisibility as _WV
from Products.CMFCore.utils import getToolByName
from bika.health.permissions import ViewPatients


class WidgetVisibility(_WV):

    def __call__(self):
        ret = super(WidgetVisibility, self).__call__()
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(ViewPatients, self.context):
            # header_table default visible fields
            ret['header_table']['visible'] += ['Patient',
                                           'PatientID',
                                           'ClientPatientID']
            # Patient related fields must be readonly, are assigned on Batch
            ret['view']['visible'] += ['Batch',
                                       'Patient',
                                       'PatientID',
                                       'ClientPatientID']
            if 'Batch' in ret['edit']['visible']:
                ret['edit']['visible'].remove('Batch')

        return ret
