from bika.lims.browser.analysisrequest.add import AnalysisRequestAddView as AnalysisRequestAddViewLIMS
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import _createObjectByType
import json
from Products.CMFCore.utils import getToolByName

class AnalysisRequestAddView(AnalysisRequestAddViewLIMS):
    """
    The main AR Add form adapted for health usage
    """
    health_template = ViewPageTemplateFile("templates/ar_add.pt")
    patient_template = ViewPageTemplateFile("templates/ar_addpatient.pt")

    def __init__(self, context, request):
        AnalysisRequestAddViewLIMS.__init__(self, context, request)
        # An array where are located all the the schema patient's fields to show on the ar_add
        self._pfields = ['PatientID', 'Surname', 'Firstname', 'BirthDate', 'Gender', 'HomePhone', 'MobilePhone',
                         'BusinessPhone', 'EmailAddress']

    def __call__(self):
        # Getting the checkbox value
        enable_bika_request_field = self.context.bika_setup.Schema().getField('EnableBikaAnalysisRequestRequestForm')
        enable_bika_request = enable_bika_request_field.get(self.context.bika_setup)
        if enable_bika_request:
            # Use the template defined on BikaLIMS
            return AnalysisRequestAddViewLIMS.__call__(self)
        else:
            # Use the Health's template
            self.request.set('disable_border', 1)
            return self.health_template()

    def get_patient_fields(self):
        """
        Get only the pateint's fields filtered by 'visibility' state
        :param visibility: The state which the fields have to be shown
        :return: a list with the filtered fields
        """
        patients_brains = getToolByName(self.context, 'bika_patient_catalog')(portal_type='Patient')
        # Only one brain is needed
        schema_fields = patients_brains[0].getObject().Schema().fields()
        #cont = getToolByName(self.context, 'bika_patient_catalog')(portal_type='Patients')
        #schema_fields = cont.portal_url.getPortalObject()["Patient"]

        fields = []
        for field in schema_fields:
            if field.required or field.getName() in self._pfields:
                fields.append(field)
        import pdb; pdb.set_trace()
        return fields

    def get_patient_context(self):
        """
        :return: The patient context
        """
        patients_brains = getToolByName(self.context, 'bika_patient_catalog')(portal_type='Patient')
        return patients_brains[0].getObject()

    def get_json_format(self, d):
        """
        Given some data, it get its json format.
        :param d: Data to be formatted.
        :return: The formatted data in JSON.
        """
        return json.dumps(d)