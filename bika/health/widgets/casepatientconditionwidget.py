from AccessControl import ClassSecurityInfo
from Products.ATExtensions.widget import RecordsWidget as ATRecordsWidget
from Products.Archetypes.Registry import registerWidget
import json


class CasePatientConditionWidget(ATRecordsWidget):
    security = ClassSecurityInfo()
    _properties = ATRecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_health_widgets/casepatientconditionwidget",
        'helper_js': ("bika_health_widgets/casepatientconditionwidget.js",),
        'helper_css': ("bika_health_widgets/casepatientconditionwidget.css",),
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        outvalues = []
        values = form.get(field.getName(), empty_marker)
        for value in values:
            outvalues.append({'Height': value.get('Height', ''),
                              'Weight': value.get('Weight', ''),
                              'Waist': value.get('Waist', '')})
        return outvalues, {}

    def jsondumps(self, val):
        return json.dumps(val)

    def getPatientCondition(self):
        conditions = [{'Height': '',
                     'Weight': '',
                     'Waist': ''}]
        return len(self.aq_parent.getPatientCondition()) > 0 \
                    and self.aq_parent.getPatientCondition() \
                    or conditions

registerWidget(CasePatientConditionWidget,
               title='CasePatientConditionWidget',
               description='Patient Condition information',)
