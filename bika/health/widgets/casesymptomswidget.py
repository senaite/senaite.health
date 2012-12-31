from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.idserver import renameAfterCreation
from Products.Archetypes.Registry import registerWidget
from bika.health.permissions import *
from bika.health.icd9cm import icd9_codes
import json
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget


class CaseSymptomsView(BrowserView):
    template = ViewPageTemplateFile("case_symptoms.pt")

    def __init__(self, context, request, fieldvalue, allow_edit):
        self.context = context
        self.request = request
        self.fieldvalue = fieldvalue
        self.allow_edit = allow_edit

    def __call__(self):
        return self.template()

    def hasSymptoms(self):
        return len(self.context.getSymptoms())>0


class CaseSymptomsWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_health_widgets/casesymptomswidget",
        'helper_js': ("bika_health_widgets/casesymptomswidget.js",),
        'helper_css': ("bika_health_widgets/casesymptomswidget.css",),
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')

    def process_form(self, instance, field, form, empty_marker=None, emptyReturnsMarker=False):
        """ Return a list of dictionaries fit for Case/Symptoms RecordsField
        """
        value = len(instance.getSymptoms())>0 and instance.getSymptoms() or []
        if 'CSY_clear' in form:
            value = []

        elif 'CSY_delete' in form:
            valueout = []
            for i in range(len(value)):
                if not ('SelectItem-%s'%i in form):
                    valueout.append(value[i])
            value = valueout

        elif 'CSY_submitted' in form:
            bsc = getToolByName(instance, 'bika_setup_catalog')
            for i in range(len(form.get('CSY_Title', []))):
                C = form['CSY_Code'][i]
                S = form['CSY_Title'][i]
                D = form['CSY_Description'][i]
                O = form['CSY_SymptomOnset'][i]

                # Create new Symptom entry if none exists (check ICD9 and setup)
                Slist = bsc(portal_type='Symptom', title=S)
                ISlist = [x for x in icd9_codes['R']
                          if x['code'] == C
                          and x['short'] == S
                          and x['long'] == D]
                if not Slist and not ISlist:
                    folder = instance.bika_setup.bika_symptoms
                    _id = folder.invokeFactory('Symptom', id='tmp')
                    obj = folder[_id]
                    obj.edit(title=S, description=D, Code=C)
                    obj.unmarkCreationFlag()
                    renameAfterCreation(obj)
                value.append({'Code': C, 'Title': S, 'Description': D, 'Onset': O})
        return value, {}

    security.declarePublic('CaseSymptoms')

    def CaseSymptoms(self, field, allow_edit=False):
        """ Prints a bika listing with current case symptoms
            field contains the archetypes field (list of dict)
        """
        # fieldvalue = getattr(field, field.accessor)()
        fieldvalue = field.get(self)
        view = CaseSymptomsView(self,
                                self.REQUEST,
                                fieldvalue=fieldvalue,
                                allow_edit=allow_edit)
        return view()

registerWidget(CaseSymptomsWidget,
               title='Case symptoms',
               description='Case symptoms',
               )
