from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.ATExtensions.widget import RecordsWidget as ATRecordsWidget
from Products.Archetypes.Registry import registerWidget
from Products.CMFCore.utils import getToolByName
from operator import itemgetter
import json


class SymptomsWidget(ATRecordsWidget):
    security = ClassSecurityInfo()
    _properties = ATRecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_health_widgets/symptomswidget",
        'helper_js': ("bika_health_widgets/symptomswidget.js",),
        'helper_css': ("bika_health_widgets/symptomswidget.css",),
        'gender': None,
        'allowDelete': False,
        'readonly': False,
        'combogrid_options': '',
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        outvalues = []
        values = form.get(field.getName(), empty_marker)
        for value in values:
            if 'Assigned' in value and int(value['Assigned']) == 1:
                outvalues.append({'UID': value['UID'],
                                  'Title': value.get('Title', ''),
                                  'Description': value.get('Description', ''),
                                  'Severity': value.get('Severity', '0'),
                                  'SeverityAllowed':value.get('SeverityAllowed', '0'),
                                  'Gender':value.get('Gender', 'dk')})
        return outvalues, {}

    def jsondumps(self, val):
        return json.dumps(val)

    def getSymptoms(self, gender=None):
        """ Returns the symptoms from the instance merged with those symptoms
            active from bika setup, with severity values assigned to default 0
        """
        outsymptoms = {}
        casesymptoms = len(self.aq_parent.getSymptoms()) > 0 \
                        and self.aq_parent.getSymptoms() or []

        casegender = 'dk'
        patientid = self.aq_parent.getPatientID()
        if patientid:
            bpc = getToolByName(self, 'bika_patient_catalog')
            patient = bpc(portal_type='Patient', ID=patientid)
            casegender = len(patient) > 0 \
                        and patient[0].getObject().getGender() or 'dk'

        symptoms = self.bika_setup_catalog(portal_type='Symptom',
                                         inactive_state='active')

        for symptom in symptoms:
            symptom = symptom.getObject()
            if not gender \
                or symptom.getGender() == 'dk' \
                or symptom.getGender() == gender:
                outsymptoms[symptom.UID()] = {'UID': symptom.UID(),
                                              'Title': symptom.Title(),
                                              'Description':symptom.Description(),
                                              'SeverityAllowed':symptom.getSeverityAllowed() and 1 or 0,
                                              'Severity':'0',
                                              'Assigned':0,
                                              'Gender':symptom.getGender(),
                                              'Visible':symptom.getGender()=='dk' or symptom.getGender()==casegender}
        for symptom in casesymptoms:
            if 'UID' in symptom:
                if symptom['UID'] in outsymptoms \
                    and ('Severity' in symptom \
                         and symptom['Severity'] is not None \
                         and symptom['Severity'] != '0'):
                    sym = outsymptoms[symptom['UID']]
                    sym['Severity'] = symptom['Severity']
                    sym['Assigned'] = 1
                else:
                    outsymptoms[symptom['UID']] = {'UID': symptom['UID'],
                                                   'Title': symptom.get('Title',''),
                                                   'Description': symptom.get('Description',''),
                                                   'SeverityAllowed': 'SeverityAllowed' in symptom and symptom['SeverityAllowed'] or 0,
                                                   'Severity': symptom.get('Severity','0'),
                                                   'Assigned': 1,
                                                   'Gender':symptom.get('Gender', 'dk'),
                                                   'Visible':symptom.get('Gender', 'dk')=='dk' or symptom.get('Gender', 'dk')==casegender}
        items=[]
        for symptom in outsymptoms.values():
            items.append(symptom)
        items.sort(lambda x, y: cmp(x['Title'].lower(), y['Title'].lower()))
        return items

registerWidget(SymptomsWidget,
               title='Symptoms',
               description='Experiencing symptoms and severity',
               )
