from bika.lims.browser.analysisrequest.add import AnalysisRequestAddView as AnalysisRequestAddViewLIMS
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AnalysisRequestAddView(AnalysisRequestAddViewLIMS):
    """
    The main AR Add form adapted for health usage
    """
    health_template = ViewPageTemplateFile("templates/ar_add.pt")
    patient_template = ViewPageTemplateFile("templates/ar_addpatient.pt")

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
