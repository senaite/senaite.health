from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.idserver import renameAfterCreation

class PatientIdentifiersView(BrowserView):
    template = ViewPageTemplateFile("patient_identifiers.pt")

    def __init__(self, context, request, fieldvalue, allow_edit):
        self.context = context
        self.request = request
        self.fieldvalue = fieldvalue
        self.allow_edit = allow_edit

    def __call__(self):
        return self.template()

    def hasIdentifiers(self):
        return len(self.context.getPatientIdentifiers())>0


class PatientIdentifiersWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_health_widgets/patientidentifierswidget",
        'helper_js': ("bika_health_widgets/patientidentifierswidget.js",),
        'helper_css': ("bika_health_widgets/patientidentifierswidget.css",),
        'read_only': False,
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None, emptyReturnsMarker=False):
        value = len(instance.getPatientIdentifiers())>0 and instance.getPatientIdentifiers() or []
        if 'PID_clear' in form:
            value = []

        elif 'PID_delete' in form:
            valueout = []
            for i in range(len(value)):
                if not ('PID_SelectItem-%s'%i in form):
                    valueout.append(value[i])
            value = valueout

        elif 'PID_submitted' in form:
            bsc = getToolByName(instance, 'bika_setup_catalog')
            for i in range(len(form.get('PID_IdentifierType', []))):
                U = form['PID_IdentifierTypeUID'][i]
                T = form['PID_IdentifierType'][i]
                D = form['PID_IdentifierTypeDescription'][i]
                I = form['PID_Identifier'][i]

                if (len(I.strip())==0):
                    instance.plone_utils.addPortalMessage(_("No identifier entered") % I, "error")
                else:
                    # Create new Identifier Type if not exists
                    if (len(T.strip())>0):
                        itlist = bsc(portal_type='IdentifierType', title=T)
                        # Just lookup from site-setup, no dynamic addition
                        # if not itlist:
                        #     folder = instance.bika_setup.bika_identifiertypes
                        #     _id = folder.invokeFactory('IdentifierType', id='tmp')
                        #     obj = folder[_id]
                        #     obj.edit(title = T, description = D)
                        #     obj.unmarkCreationFlag()
                        #     renameAfterCreation(obj)

                value.append({'IdentifierTypeUID':U, 'IdentifierType': T, 'Identifier': I, 'IdentifierTypeDescription': D })
        return value, {}

    security.declarePublic('PatientIdentifiers')
    def PatientIdentifiers(self, field, allow_edit=False):
        fieldvalue = getattr(field, field.accessor)()
        view = PatientIdentifiersView(self,
                                self.REQUEST,
                                fieldvalue=fieldvalue,
                                allow_edit=allow_edit)
        return view()


registerWidget(PatientIdentifiersWidget,
               title=_('Patient identifiers'),
               description=_("Patient additional identifiers"),)
