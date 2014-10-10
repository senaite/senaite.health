from Products.ATContentTypes.content import schemata
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.utils import DT2dt
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.lims.browser.fields import AddressField
from bika.lims.browser.widgets import AddressWidget
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import RecordsWidget
from bika.health.widgets import SplittedDateWidget
from bika.health.config import *
from bika.lims.content.person import Person
from bika.health.interfaces import IPatient
from bika.health.permissions import *
from bika.health.widgets import ReadonlyStringWidget
from datetime import datetime
from zope.interface import implements
from bika.health.widgets.patientmenstrualstatuswidget import PatientMenstrualStatusWidget

schema = Person.schema.copy() + Schema((
    StringField('PatientID',
                searchable=1,
                required=0,
                widget=ReadonlyStringWidget(
                    visible={'view': 'visible', 'edit': 'hidden'},
                    label=_('Patient ID'),
                    css='readonly-emphasize',
                ),
    ),
    ReferenceField('PrimaryReferrer',
                   vocabulary='get_clients',
                   allowed_types=('Client',),
                   relationship='PatientClient',
                   required=1,
                   widget=SelectionWidget(
                       format='select',
                       label=_('Client'),
                   ),
    ),
    ComputedField('PrimaryReferrerTitle',
                  expression="context.Schema()['PrimaryReferrer'].get(context) and context.Schema()['PrimaryReferrer'].get(context).Title() or None",
                  widget=ComputedWidget(
                  ),
    ),
     ComputedField('PrimaryReferrerUID',
                  expression="context.Schema()['PrimaryReferrer'].get(context) and context.Schema()['PrimaryReferrer'].get(context).UID() or None",
                  widget=ComputedWidget(
                  ),
    ),
    StringField('Gender',
                vocabulary=GENDERS,
                index='FieldIndex',
                default='dk',
                widget=SelectionWidget(
                    format='select',
                    label=_('Gender'),
                ),
    ),
    StringField('Age',
                widget=StringWidget(
                    label=_('Age'),
                    visible=0,
                    width=3,
                ),
    ),
    DateTimeField('BirthDate',
                  required=0,
                  widget=DateTimeWidget(
                      label=_('Birth date'),
                  ),
    ),
    BooleanField('BirthDateEstimated',
                 default=False,
                 widget=BooleanWidget(
                     label=_('Birth date is estimated'),
                 ),
    ),
    RecordsField('AgeSplitted',
                 required=1,
                 widget=SplittedDateWidget(
                     label=_('Age'),
                 ),
    ),
    AddressField('CountryState',
                 widget=AddressWidget(
                 label=_("Country and state"),
                     showLegend=True,
                     showDistrict=False,
                     showCopyFrom=False,
                     showCity=False,
                     showPostalCode=False,
                     showAddress=False,
                 ),
    ),
    RecordsField('PatientIdentifiers',
                 type='patientidentifiers',
                 subfields=('IdentifierType',
                            'Identifier'),
                 subfield_labels={'IdentifierType': _('Identifier Type'),
                                  'Identifier': _('Identifier')},
                 subfield_sizes={'Identifier': 15,
                                 'Identifier Type': 25},
                 widget=RecordsWidget(
                 label=_('Additional identifiers'),
                 description=_('Patient additional identifiers'),
                     combogrid_options={
                         'IdentifierType': {
                             'colModel': [{'columnName':'IdentifierType', 'width':'30', 'label':_('Title')},
                                          {'columnName':'Description', 'width':'70', 'label':_('Description')}],
                             'url': 'getidentifiertypes',
                             'showOn': True,
                             'width': '550px'
                         },
                     },
                 ),
    ),
    TextField('Remarks',
              searchable=True,
              default_content_type='text/plain',
              allowable_content_types = ('text/plain', ),
              default_output_type="text/plain",
                  widget=TextAreaWidget(
                      macro="bika_widgets/remarks",
                  label=_('Remarks'),
                  append_only=True,
              ),
    ),
    RecordsField('TreatmentHistory',
                 type='treatmenthistory',
                 subfields=('Treatment',
                            'Drug',
                            'Start',
                            'End'),
                 required_subfields=('Drug',
                                     'Start',
                                     'End'),
                 subfield_labels={'Drug': _('Drug'),
                                  'Start': _('Start'),
                                  'End': _('End')},
                 subfield_sizes={'Drug': 40,
                                 'Start': 10,
                                 'End': 10},
                 subfield_types={'Start': 'datepicker_nofuture',
                                 'End': 'datepicker'},
                 widget=RecordsWidget(
                 label='Drug History',
                 description=_("A list of patient treatments and drugs administered."),
                     combogrid_options={
                         'Drug': {
                             'colModel': [{'columnName':'Drug', 'width':'30', 'label':_('Title')},
                                          {'columnName':'Description', 'width':'70', 'label':_('Description')}],
                             'url': 'getdrugs',
                             'showOn': True,
                             'width': '550px'
                         },
                     },
                 ),
    ),
    RecordsField('Allergies',
                 type='allergies',
                 subfields=('DrugProhibition',
                            'Drug',
                            'Remarks'),
                 required_subfields=('DrugProhibition',
                                     'Drug'),
                 subfield_labels={'DrugProhibition': _('Drug Prohibition Explanation'),
                                  'Drug': _('Drug'),
                                  'Remarks': _('Remarks')},
                 subfield_sizes={'DrugProhibition': 30,
                                 'Drug': 30,
                                 'Remarks': 30},
                 widget=RecordsWidget(
                     label='Allergies',
                     description=_("Known Patient allergies to keep information that can aid drug reaction interpretation"),
                     combogrid_options={
                         'Drug': {
                             'colModel': [{'columnName':'Title', 'width':'30', 'label':_('Title')},
                                          {'columnName':'Description', 'width':'70', 'label':_('Description')}],
                             'url': 'getdrugs',
                             'showOn': True,
                             'width': '550px'
                         },
                         'DrugProhibition': {
                             'colModel': [{'columnName':'DrugProhibition', 'width':'30', 'label':_('Title')},
                                          {'columnName':'Description', 'width':'70', 'label':_('Description')}],
                             'url': 'getdrugprohibitions',
                             'showOn': True,
                             'width': '550px'
                         },
                     },
                 ),
    ),
    RecordsField('ImmunizationHistory',
                 type='immunizationhistory',
                 subfields=('EPINumber',
                            'Immunization',
                            'VaccinationCenter',
                            'Date',
                            'Remarks'),
                 required_subfields=('EPINumber',
                                     'Immunization',
                                     'Date'),
                 subfield_labels={'EPINumber': _('EPI Number'),
                                  'Immunization': _('Immunization'),
                                  'VaccinationCenter': _('Vaccination Center'),
                                  'Date': _('Date'),
                                  'Remarks': _('Remarks')},
                 subfield_sizes={'EPINumber': 12,
                                 'Immunization': 20,
                                 'VaccinationCenter': 10, 'Date': 10, 'Remarks': 25},
                 subfield_types={'Date':'datepicker_nofuture'},
                 widget=RecordsWidget(
                     label='Immunization History',
                     description=_("A list of immunizations administered to the patient."),
                     combogrid_options={
                         'Immunization': {
                             'colModel': [{'columnName':'Immunization', 'width':'30', 'label':_('Title')},
                                         {'columnName':'Description', 'width':'70', 'label':_('Description')}],
                             'url': 'getimmunizations',
                             'showOn': True,
                             'width': '550px'
                         },
                         'VaccinationCenter': {
                             'colModel': [{'columnName':'VaccinationCenter', 'width':'100', 'label':_('Title')}],
                             'url': 'getvaccinationcenters',
                             'showOn': True,
                             'width': '550px'
                         },
                     },
                 ),
    ),
    RecordsField('TravelHistory',
                 type='travelhistory',
                 subfields=('TripStartDate',
                            'TripEndDate',
                            'Country',
                            'Location',
                            'Remarks'),
                 required_subfields=('Country'),
                 subfield_labels={'TripStartDate': _('Trip Start Date', 'Start date'),
                                  'TripEndDate': _('Trip End Date', 'End date'),
                                  'Country': _('Country'),
                                  'Location': _('Location'),
                                  'Remarks': _('Remarks')},
                 subfield_sizes={'TripStartDate': 10,
                                 'TripEndDate': 10,
                                 'Country': 20,
                                 'Location': 20,
                                 'Remarks': 25},
                 subfield_types={'TripStartDate':'datepicker_nofuture',
                                 'TripEndDate':'datepicker'},
                 widget=RecordsWidget(
                     label='Travel History',
                     description=_("A list of places visited by the patient."),
                     combogrid_options={
                         'Country': {
                             'colModel': [{'columnName':'Code', 'width':'15', 'label':_('Code')},
                                          {'columnName':'Country', 'width':'85', 'label':_('Country')}],
                             'url': 'getCountries',
                             'showOn': True,
                             'width': "450px",
                         },
                     },
                 ),
    ),
    RecordsField('ChronicConditions',
                 type='chronicconditions',
                 subfields=('Code',
                            'Title',
                            'Description',
                            'Onset',
                            'End'),
                 required_subfields=('Title',
                                     'Onset'),
                 subfield_sizes={'Code': 7,
                                 'Title': 20,
                                 'Description': 35,
                                 'Onset': 10,
                                 'End': 10},
                 subfield_types={'Onset': 'datepicker_nofuture',
                                 'End': 'datepicker'},
                 widget=RecordsWidget(
                     label='Past Medical History',
                     description=_("Patient's past medical history."),
                     combogrid_options={
                         'Title': {
                             'colModel': [{'columnName':'Code', 'width':'10', 'label':_('Code')},
                                          {'columnName':'Title', 'width':'30', 'label':_('Title')},
                                          {'columnName':'Description', 'width':'60', 'label':_('Description')}],
                             'url': 'getdiseases',
                             'showOn': True,
                             'width': "650px",
                         },
                     },
                 ),
    ),
    StringField('BirthPlace', schemata='Personal',
                widget=StringWidget(
                    label=_('Birth place'),
                ),
    ),
    StringField('Ethnicity', schemata='Personal',
                index='FieldIndex',
                vocabulary=ETHNICITIES,
                widget=ReferenceWidget(
                    label=_('Ethnicity'),
                    description=_("Ethnicity eg. Asian, African, etc."),
                ),
    ),
    StringField('Citizenship', schemata='Personal',
                widget=StringWidget(
                    label=_('Citizenship'),
                ),
    ),
    StringField('MothersName', schemata='Personal',
                widget=StringWidget(
                    label=_('Mothers name'),
                ),
    ),
    StringField('CivilStatus', schemata='Personal',
                widget=StringWidget(
                    label=_('Civil status'),
                ),
    ),
    ImageField('Photo', schemata='Identification',
               widget=ImageWidget(
                   label=_('Photo'),
               ),
    ),
    ImageField('Feature', schemata='Identification',
               multiValue=1,
               widget=ImageWidget(
                   label=_('Feature'),
               ),
    ),
    RecordsField('MenstrualStatus',
            type='menstrualstatus',
            widget=PatientMenstrualStatusWidget(
                label='Menstrual status',
            ),
    ),
    StringField('ClientPatientID',
            searchable=1,
            required=0,
            widget=StringWidget(
                label=_('Client Patient ID'),
            ),
    ),
    BooleanField('Anonymous',
             default=False,
             widget=BooleanWidget(
                 label=_("Anonymous")
             ),
    ),
    BooleanField('DefaultResultsDistribution',
        schemata="Publication preference",
        default=True,
        widget=BooleanWidget(
            label=_("Inherit default settings"),
            description=_("If checked, settings will be inherited from "
                          "the Client, so further changes in Client for this "
                          "setting will be populated too."))
    ),
    BooleanField('AllowResultsDistribution',
        schemata="Publication preference",
        default=False,
        widget=BooleanWidget(
            label=_("Allow results distribution to this patient"),
            description=_("If checked, results reports will also be sent "
                          "to the Patient automatically."))
    ),
    LinesField('PublicationPreferences',
        vocabulary=PUBLICATION_PREFS,
        schemata='Publication preference',
        widget=MultiSelectionWidget(
            label=_("Publication preference"),
            description=_("Select the preferred channels to be used for "
                          "sending the results reports to this Patient."))
    ),
    BooleanField('PublicationAttachmentsPermitted',
        default=False,
        schemata='Publication preference',
        widget=BooleanWidget(
            label=_("Results attachments permitted"),
            description=_("File attachments to results, e.g. microscope "
                          "photos, will be included in emails to patient "
                          "if this option is enabled"))
    ),
))

schema['JobTitle'].widget.visible = False
schema['Department'].widget.visible = False
schema['BusinessPhone'].widget.visible = False
schema['BusinessFax'].widget.visible = False
# Don't make title required - it will be computed from the Person's Fullname
schema['title'].required = 0
schema['title'].widget.visible = False
schema['EmailAddress'].schemata = 'Personal'
schema['HomePhone'].schemata = 'Personal'
schema['MobilePhone'].schemata = 'Personal'
#schema.moveField('PatientID', pos='top')
schema.moveField('PrimaryReferrer', after='Surname')
schema.moveField('PatientID', before='title')
schema.moveField('PatientIdentifiers', after='PrimaryReferrer')
schema.moveField('Gender', after='PatientIdentifiers')
schema.moveField('Age', after='Gender')
schema.moveField('BirthDate', after='Age')
schema.moveField('BirthDateEstimated', after='BirthDate')
schema.moveField('AgeSplitted', after='BirthDateEstimated')
schema.moveField('CountryState', after='AgeSplitted')
schema.moveField('MenstrualStatus', after='AgeSplitted')
schema.moveField('ClientPatientID', after='PatientID')
schema.moveField('Anonymous', before='ClientPatientID')


class Patient(Person):
    implements(IPatient)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Fullname as title """
        return safe_unicode(self.getFullname()).encode('utf-8')

    security.declarePublic('getPatientID')

    def getPatientID(self):
        return self.getId()

    security.declarePublic('getSamples')
    def getSamples(self):
        """ get all samples taken from this Patient """
        return [ar.getSample() for ar in self.getARs() if ar.getSample()]

    security.declarePublic('getARs')
    def getARs(self, analysis_state=None):
        bc = getToolByName(self, 'bika_catalog')
        ars = bc(portal_type='AnalysisRequest')
        outars = []
        for ar in ars:
            ar = ar.getObject()
            pat = ar.Schema()['Patient'].get(ar) if ar else None
            if pat and pat.UID() == self.UID():
                outars.append(ar)
        return outars

    def get_clients(self):
        ## Only show clients to which we have Manage AR rights.
        mtool = getToolByName(self, 'portal_membership')
        clientfolder = self.clients
        clients = []
        for client in clientfolder.objectValues("Client"):
            if not mtool.checkPermission(ManageAnalysisRequests, client):
                continue
            clients.append([client.UID(), client.Title()])
        clients.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        clients.insert(0, ['', ''])
        return DisplayList(clients)

    def getPatientIdentifiersStr(self):
        ids = self.getPatientIdentifiers()
        idsstr = ''
        for id in ids:
            idsstr += idsstr == '' and id['Identifier'] or (', ' + id['Identifier'])
        return idsstr
        #return self.getSendersPatientID()+" "+self.getSendersCaseID()+" "+self.getSendersSpecimenID()

    def getPatientIdentifiersStrHtml(self):
        ids = self.getPatientIdentifiers()
        idsstr = '<table cellpadding="0" cellspacing="0" border="0" class="patientsidentifiers" style="text-align:left;width: 100%;"><tr><td>'
        for id in ids:
            idsstr += "<tr><td>" + id['IdentifierType'] + ':</td><td>' + id['Identifier'] + "</td></tr>"
        return "</table>" + idsstr

    def getAgeSplitted(self):

        if (self.getBirthDate()):
            dob = DT2dt(self.getBirthDate()).replace(tzinfo=None)
            now = datetime.today()

            currentday = now.day
            currentmonth = now.month
            currentyear = now.year
            birthday = dob.day
            birthmonth = dob.month
            birthyear = dob.year
            ageday = currentday - birthday
            agemonth = 0
            ageyear = 0
            months31days = [1, 3, 5, 7, 8, 10, 12]

            if (ageday < 0):
                currentmonth -= 1
                if (currentmonth < 1):
                    currentyear -= 1
                    currentmonth = currentmonth + 12

                dayspermonth = 30
                if currentmonth in months31days:
                    dayspermonth = 31
                elif currentmonth == 2:
                    dayspermonth = 28
                    if(currentyear % 4 == 0
                       and (currentyear % 100 > 0 or currentyear % 400 == 0)):
                        dayspermonth += 1

                ageday = ageday + dayspermonth

            agemonth = currentmonth - birthmonth
            if (agemonth < 0):
                currentyear -= 1
                agemonth = agemonth + 12

            ageyear = currentyear - birthyear

            return [{'year': ageyear,
                    'month': agemonth,
                    'day': ageday}]
        else:
            return [{'year': '',
                    'month': '',
                    'day': ''}]

    def getAge(self):
        return self.getAgeSplitted()[0]['year']

    def getAgeSplittedStr(self):
        splitted = self.getAgeSplitted()[0]
        arr = []
        arr.append(splitted['year'] and str(splitted['year']) + 'y' or '')
        arr.append(splitted['month'] and str(splitted['month']) + 'm' or '')
        arr.append(splitted['day'] and str(splitted['day']) + 'd' or '')
        return ' '.join(arr)

    def setCountryState(self, value):
        pa = self.getPhysicalAddress() and self.getPhysicalAddress() or {'country': '', 'state': ''}
        pa['country'] = self.REQUEST.form.get('CountryState', {'country': ''})['country']
        pa['state'] = self.REQUEST.form.get('CountryState', {'state': ''})['state']
        if not pa['country']:
            return

        return self.setPhysicalAddress(pa)

    def getCountryState(self):
        return self.getPhysicalAddress()

# schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(Patient, PROJECTNAME)
