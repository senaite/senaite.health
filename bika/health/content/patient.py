# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
from bika.lims.browser.fields import DateTimeField as DateTimeField_bl
from bika.lims.browser.widgets import AddressWidget
from bika.lims.browser.widgets import DateTimeWidget as DateTimeWidget_bl
from bika.lims.browser.widgets import RecordsWidget
from bika.health.widgets import SplittedDateWidget
from bika.health.config import *
from bika.lims.content.person import Person
from bika.health.interfaces import IPatient
from bika.health.permissions import *
from bika.health.widgets import ReadonlyStringWidget
from datetime import datetime
from zope.component import getAdapters
from zope.interface import implements
from Products.Archetypes.references import HoldingReference
from bika.health.widgets.patientmenstrualstatuswidget import PatientMenstrualStatusWidget
from bika.lims.vocabularies import CustomPubPrefVocabularyFactory

schema = Person.schema.copy() + Schema((
    StringField(
        'PatientID',
        searchable=1,
        required=0,
        widget=ReadonlyStringWidget(
            visible={'view': 'visible', 'edit': 'hidden'},
            label=_('Patient ID'),
            css='readonly-emphasize',
        ),
    ),
    ReferenceField(
        'PrimaryReferrer',
        vocabulary='get_clients',
        allowed_types=('Client',),
        relationship='PatientClient',
        required=1,
        widget=SelectionWidget(
            format='select',
            label=_('Client'),
        ),
    ),
    ComputedField(
        'PrimaryReferrerID',
        expression="context.Schema()['PrimaryReferrer'].get(context) and context.Schema()['PrimaryReferrer'].get(context).getId() or None",
        widget=ComputedWidget(
        ),
    ),
    ComputedField(
        'PrimaryReferrerTitle',
        expression="context.Schema()['PrimaryReferrer'].get(context) and context.Schema()['PrimaryReferrer'].get(context).Title() or None",
        widget=ComputedWidget(
        ),
    ),
    ComputedField(
        'PrimaryReferrerUID',
        expression="context.Schema()['PrimaryReferrer'].get(context) and context.Schema()['PrimaryReferrer'].get(context).UID() or None",
        widget=ComputedWidget(
        ),
    ),
    ComputedField(
        'PrimaryReferrerURL',
        expression="context.getPrimaryReferrer().absolute_url_path() if context.getPrimaryReferrer() else ''",
        widget=ComputedWidget(
            visible=False
        ),
    ),
    StringField(
        'Gender',
        vocabulary=GENDERS,
        index='FieldIndex',
        default='dk',
        widget=SelectionWidget(
            format='select',
            label=_('Gender'),
        ),
    ),
    StringField(
        'Age',
        widget=StringWidget(
            label=_('Age'),
            visible=0,
            width=3,
        ),
    ),
    DateTimeField_bl(
        'BirthDate',
        required=0,
        validators=('isDateFormat',),
        widget=DateTimeWidget_bl(
            label=_('Birth date'),
            datepicker_nofuture=1,
        ),
    ),
    BooleanField(
        'BirthDateEstimated',
        default=False,
        widget=BooleanWidget(
            label=_('Birth date is estimated'),
        ),
    ),
    RecordsField(
        'AgeSplitted',
        required=1,
        widget=SplittedDateWidget(
            label=_('Age'),
        ),
    ),
    ComputedField(
        'AgeSplittedStr',
        expression="context.getAgeSplittedStr()",
        widget=ComputedWidget(
            visible=False
        ),
    ),
    AddressField(
        'CountryState',
        widget=AddressWidget(
            searchable=True,
            label=_("Country and state"),
            showLegend=True,
            showDistrict=True,
            showCopyFrom=False,
            showCity=False,
            showPostalCode=False,
            showAddress=False,
        ),
    ),
    RecordsField(
        'PatientIdentifiers',
        type='patientidentifiers',
        subfields=(
            'IdentifierType',
            'Identifier'
        ),
        subfield_labels={
            'IdentifierType': _('Identifier Type'),
            'Identifier': _('Identifier')
        },
        subfield_sizes={
            'Identifier': 15,
            'Identifier Type': 25
        },
        widget=RecordsWidget(
            label=_('Additional identifiers'),
            description=_('Patient additional identifiers'),
            combogrid_options={
                'IdentifierType': {
                    'colModel': [
                        {
                            'columnName': 'IdentifierType',
                            'width': '30',
                            'label': _('Title')
                        },
                        {
                            'columnName': 'Description',
                            'width': '70',
                            'label': _('Description')
                        }
                    ],
                    'url': 'getidentifiertypes',
                    'showOn': True,
                    'width': '550px'
                },
            },
        ),
    ),
    ComputedField(
        'PatientIdentifiersStr',
        expression="context.getPatientIdentifiersStr()",
        widget=ComputedWidget(
            visible=False
        ),
    ),
    TextField(
        'Remarks',
        searchable=True,
        default_content_type='text/plain',
        allowable_content_types=('text/plain', ),
        default_output_type="text/plain",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_('Remarks'),
            append_only=True,
        ),
    ),
    RecordsField(
        'TreatmentHistory',
        type='treatmenthistory',
        subfields=(
            'Treatment',
            'Drug',
            'Start',
            'End'
        ),
        required_subfields=(
            'Drug',
            'Start',
            'End'
        ),
        subfield_labels={
            'Drug': _('Drug'),
            'Start': _('Start'),
            'End': _('End')
        },
        subfield_sizes={
            'Drug': 40,
            'Start': 10,
            'End': 10
        },
        subfield_types={
            'Start': 'datepicker_nofuture',
            'End': 'datepicker'
        },
        widget=RecordsWidget(
            label='Drug History',
            description=_("A list of patient treatments and drugs administered."),
            combogrid_options={
                'Treatment': {
                    'colModel': [
                        {
                            'columnName': 'Treatment',
                            'width': '30',
                            'label': _('Title')
                        },
                        {
                            'columnName': 'Description',
                            'width': '70',
                            'label': _('Description')
                        }
                    ],
                    'url': 'gettreatments',
                    'showOn': True,
                    'width': '550px'
                },
                'Drug': {
                    'colModel': [
                        {
                            'columnName': 'Drug',
                            'width': '30',
                            'label': _('Title')
                        },
                        {
                            'columnName': 'Description',
                            'width': '70',
                            'label': _('Description')
                        }
                    ],
                    'url': 'getdrugs',
                    'showOn': True,
                    'width': '550px'
                },
            },
        ),
    ),
    RecordsField(
        'Allergies',
        type='allergies',
        subfields=(
            'DrugProhibition',
            'Drug',
            'Remarks'
        ),
        required_subfields=(
            'DrugProhibition',
            'Drug'
        ),
        subfield_labels={
            'DrugProhibition': _('Drug Prohibition Explanation'),
            'Drug': _('Drug'),
            'Remarks': _('Remarks')
        },
        subfield_sizes={
            'DrugProhibition': 30,
            'Drug': 30,
            'Remarks': 30
        },
        widget=RecordsWidget(
            label='Allergies',
            description=_("Known Patient allergies to keep information that can aid drug reaction interpretation"),
            combogrid_options={
                'Drug': {
                    'colModel': [
                        {
                            'columnName': 'Title',
                            'width': '30',
                            'label': _('Title')
                        },
                        {
                            'columnName': 'Description',
                            'width': '70',
                            'label': _('Description')
                        }
                    ],
                    'url': 'getdrugs',
                    'showOn': True,
                    'width': '550px'
                },
                'DrugProhibition': {
                    'colModel': [
                        {
                            'columnName': 'DrugProhibition',
                            'width': '30',
                            'label': _('Title')
                        },
                        {
                            'columnName': 'Description',
                            'width': '70',
                            'label': _('Description')
                        }
                    ],
                    'url': 'getdrugprohibitions',
                    'showOn': True,
                    'width': '550px'
                },
            },
        ),
    ),
    RecordsField(
        'ImmunizationHistory',
        type='immunizationhistory',
        subfields=(
            'EPINumber',
            'Immunization',
            'VaccinationCenter',
            'Date',
            'Remarks'
        ),
        required_subfields=(
            'EPINumber',
            'Immunization',
            'Date'
        ),
        subfield_labels={
            'EPINumber': _('EPI Number'),
            'Immunization': _('Immunization'),
            'VaccinationCenter': _('Vaccination Center'),
            'Date': _('Date'),
            'Remarks': _('Remarks')
        },
        subfield_sizes={
            'EPINumber': 12,
            'Immunization': 20,
            'VaccinationCenter': 10,
            'Date': 10,
            'Remarks': 25
        },
        subfield_types={
            'Date': 'datepicker_nofuture'
        },
        widget=RecordsWidget(
            label='Immunization History',
            description=_("A list of immunizations administered to the patient."),
            combogrid_options={
                'Immunization': {
                    'colModel': [
                        {
                            'columnName': 'Immunization',
                            'width': '30',
                            'label': _('Title')
                        },
                        {
                            'columnName': 'Description',
                            'width': '70',
                            'label': _('Description')
                        }
                    ],
                    'url': 'getimmunizations',
                    'showOn': True,
                    'width': '550px'
                },
                'VaccinationCenter': {
                    'colModel': [
                        {
                            'columnName': 'VaccinationCenter',
                            'width': '100',
                            'label': _('Title')
                        }
                    ],
                    'url': 'getvaccinationcenters',
                    'showOn': True,
                    'width': '550px'
                },
            },
        ),
    ),
    RecordsField(
        'TravelHistory',
        type='travelhistory',
        subfields=(
            'TripStartDate',
            'TripEndDate',
            'Country',
            'Location',
            'Remarks'
        ),
        required_subfields='Country',
        subfield_labels={
            'TripStartDate': _('Trip Start Date', 'Start date'),
            'TripEndDate': _('Trip End Date', 'End date'),
            'Country': _('Country'),
            'Location': _('Location'),
            'Remarks': _('Remarks')},
        subfield_sizes={
            'TripStartDate': 10,
            'TripEndDate': 10,
            'Country': 20,
            'Location': 20,
            'Remarks': 25},
        subfield_types={
            'TripStartDate': 'datepicker_nofuture',
            'TripEndDate': 'datepicker'
        },
        widget=RecordsWidget(
            label='Travel History',
            description=_("A list of places visited by the patient."),
            combogrid_options={
                'Country': {
                    'colModel': [
                        {
                            'columnName': 'Code',
                            'width': '15',
                            'label': _('Code')
                        },
                        {
                            'columnName': 'Country',
                            'width': '85',
                            'label': _('Country')
                        }
                    ],
                    'url': 'getCountries',
                    'showOn': True,
                    'width': "450px",
                },
            },
        ),
    ),
    RecordsField(
        'ChronicConditions',
        type='chronicconditions',
        subfields=(
            'Code',
            'Title',
            'Description',
            'Onset',
            'End'
        ),
        required_subfields=(
            'Title',
            'Onset'
        ),
        subfield_sizes={
            'Code': 7,
            'Title': 20,
            'Description': 35,
            'Onset': 10,
            'End': 10
        },
        subfield_types={
            'Onset': 'datepicker_nofuture',
            'End': 'datepicker'
        },
        widget=RecordsWidget(
            label='Past Medical History',
            description=_("Patient's past medical history."),
            combogrid_options={
                'Title': {
                    'colModel': [
                        {
                            'columnName': 'Code',
                            'width': '10',
                            'label': _('Code')
                        },
                        {
                            'columnName': 'Title',
                            'width': '30',
                            'label': _('Title')
                        },
                        {
                            'columnName': 'Description',
                            'width': '60',
                            'label': _('Description')
                        }
                    ],
                    'url': 'getdiseases',
                    'showOn': True,
                    'width': "650px",
                },
            },
        ),
    ),
    StringField(
        'BirthPlace',
        schemata='Personal',
        widget=StringWidget(
            label=_('Birth place'),
        ),
    ),
    # TODO This field will be removed on release 319. We maintain this field on release 318
    # because of the transference between string field and content type data.
    StringField(
        'Ethnicity',
        schemata='Personal',
        index='FieldIndex',
        vocabulary=ETHNICITIES,
        widget=ReferenceWidget(
            label=_('Ethnicity'),
            description=_("Ethnicity eg. Asian, African, etc."),
            visible=False,
        ),
    ),
    # TODO This field will change its name on v319 and it'll be called Ethnicity
    ReferenceField(
        'Ethnicity_Obj',
        schemata='Personal',
        vocabulary='getEthnicitiesVocabulary',
        allowed_types=('Ethnicity',),
        relationship='PatientEthnicity',
        widget=SelectionWidget(
            format='select',
            label=_('Ethnicity'),
            description=_("Ethnicity eg. Asian, African, etc."),
        ),
    ),
    StringField(
        'Citizenship',
        schemata='Personal',
        widget=StringWidget(
            label=_('Citizenship'),
        ),
    ),
    StringField(
        'MothersName',
        schemata='Personal',
        widget=StringWidget(
            label=_('Mothers name'),
        ),
    ),
    StringField(
        'FathersName',
        schemata='Personal',
        widget=StringWidget(
            label=_('Fathers name'),
        ),
    ),
    StringField(
        'CivilStatus',
        schemata='Personal',
        widget=StringWidget(
            label=_('Civil status'),
        ),
    ),
    ImageField(
        'Photo',
        schemata='Identification',
        widget=ImageWidget(
            label=_('Photo'),
        ),
    ),
    ImageField(
        'Feature',
        schemata='Identification',
        multiValue=1,
        widget=ImageWidget(
            label=_('Feature'),
        ),
    ),
    RecordsField(
        'MenstrualStatus',
        type='menstrualstatus',
        widget=PatientMenstrualStatusWidget(
            label='Menstrual status',
        ),
    ),
    StringField(
        'ClientPatientID',
        searchable=1,
        validators=('unique_client_patient_ID_validator',),
        required=1,
        widget=StringWidget(
            label=_('Client Patient ID'),
        ),
    ),
    BooleanField(
        'Anonymous',
        default=False,
        widget=BooleanWidget(
            label=_("Anonymous")
        ),
    ),
    BooleanField(
        'DefaultResultsDistribution',
        schemata="Publication preference",
        default=True,
        widget=BooleanWidget(
            label=_("Inherit default settings"),
            description=_("If checked, settings will be inherited from "
                          "the Client, so further changes in Client for this "
                          "setting will be populated too."))
    ),
    BooleanField(
        'AllowResultsDistribution',
        schemata="Publication preference",
        default=False,
        widget=BooleanWidget(
            label=_("Allow results distribution to this patient"),
            description=_("If checked, results reports will also be sent "
                          "to the Patient automatically."))
    ),
    LinesField(
        'PublicationPreferences',
        vocabulary_factory='bika.lims.vocabularies.CustomPubPrefVocabularyFactory',
        schemata='Publication preference',
        widget=MultiSelectionWidget(
            label=_("Publication preference"),
            description=_("Select the preferred channels to be used for "
                          "sending the results reports to this Patient."))
    ),
    BooleanField(
        'PublicationAttachmentsPermitted',
        default=False,
        schemata='Publication preference',
        widget=BooleanWidget(
            label=_("Results attachments permitted"),
            description=_("File attachments to results, e.g. microscope "
                          "photos, will be included in emails to patient "
                          "if this option is enabled"))
    ),
    ReferenceField(
        'InsuranceCompany',
        vocabulary='get_insurancecompanies',
        allowed_types=('InsuranceCompany',),
        relationship='InsuranceCompany',
        required=False,
        widget=SelectionWidget(
            format='select',
            label=_('Insurance Company'),
            ),
        ),
    StringField(
        'InsuranceNumber',
        searchable=1,
        required=0,
        widget=StringWidget(
            label=_('Insurance Number'),
        ),
    ),
    BooleanField(
        'InvoiceToInsuranceCompany',
        default=False,
        widget=BooleanWidget(
            label=_("Send invoices to the insurance company."),
            description=_("If it is checked the invoices will be send to the insurance company."
                          " In this case the insurance number will be mandatory."))
    ),
    BooleanField(
        'PatientAsGuarantor',
        schemata='Insurance',
        default=True,
        widget=BooleanWidget(
            label=_("The patient is the guarantor."),
            description=_("The patient and the guarantor are the same."))
    ),
    StringField(
        'GuarantorID',
        searchable=1,
        schemata='Insurance',
        required=0,
        widget=StringWidget(
            label=_('Guarantor ID'),
            description=_("The ID number (Insurance Number) from the person whose contract cover the current patient.")
        ),
    ),
    StringField(
        'GuarantorSurname',
        searchable=1,
        schemata='Insurance',
        required=0,
        widget=StringWidget(
            label=_("Guarantor's Surname"),
        ),
    ),
    StringField(
        'GuarantorFirstname',
        searchable=1,
        schemata='Insurance',
        required=0,
        widget=StringWidget(
            label=_("Guarantor's First Name"),
        ),
    ),
    AddressField(
        'GuarantorPostalAddress',
        searchable=1,
        schemata='Insurance',
        required=0,
        widget=AddressWidget(
            label=_("Guarantor's postal address"),
        ),
    ),
    StringField(
        'GuarantorBusinessPhone',
        schemata='Insurance',
        widget=StringWidget(
            label=_("Guarantor's Phone (business)"),
        ),
    ),
    StringField(
        'GuarantorHomePhone',
        schemata='Insurance',
        widget=StringWidget(
            label=_("Guarantor's Phone (home)"),
        ),
    ),
    StringField(
        'GuarantorMobilePhone',
        schemata='Insurance',
        widget=StringWidget(
            label=_("Guarantor's Phone (mobile)"),
        ),
    ),
    BooleanField(
        'ConsentSMS',
        default=False,
        widget=BooleanWidget(
            label=_('Consent to SMS'),
        ),
    ),
    ComputedField(
        'NumberOfSamples',
        expression="len(context.getSamples())",
        widget=ComputedWidget(
            visible=False
        ),
    ),
    ComputedField(
        'NumberOfSamplesCancelled',
        expression="len(context.getSamplesCancelled())",
        widget=ComputedWidget(
            visible=False
        ),
    ),
    ComputedField(
        'NumberOfSamplesOngoing',
        expression="len(context.getSamplesOngoing())",
        widget=ComputedWidget(
            visible=False
        ),
    ),
    ComputedField(
        'NumberOfSamplesPublished',
        expression="len(context.getSamplesPublished())",
        widget=ComputedWidget(
            visible=False
        ),
    ),
    ComputedField(
        'RatioOfSamplesOngoing',
        expression="context.getNumberOfSamplesOngoingRatio()",
        widget=ComputedWidget(
            visible=False
        ),
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
schema['InsuranceCompany'].schemata = 'Insurance'
schema['InsuranceNumber'].schemata = 'Insurance'
schema['InvoiceToInsuranceCompany'].schemata = 'Insurance'
schema.moveField('PrimaryReferrer', after='Surname')
schema.moveField('PatientID', before='title')
schema.moveField('ClientPatientID', after='PatientID')
schema.moveField('Anonymous', before='ClientPatientID')
schema.moveField('InsuranceCompany', after='PrimaryReferrer')
schema.moveField('InsuranceNumber', after='InsuranceCompany')
schema.moveField('PatientIdentifiers', after='InsuranceNumber')
schema.moveField('Gender', after='PatientIdentifiers')
schema.moveField('Age', after='Gender')
schema.moveField('BirthDate', after='Age')
schema.moveField('BirthDateEstimated', after='BirthDate')
schema.moveField('AgeSplitted', after='BirthDateEstimated')
schema.moveField('CountryState', after='AgeSplitted')
schema.moveField('MenstrualStatus', after='AgeSplitted')
schema.moveField('ConsentSMS', after='PrimaryReferrer')


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
        samples = []
        for ar in self.getARs():
            sample = ar.getObject().getSample()
            if sample:
                samples.append(sample)
        return samples

    def getSamplesCancelled(self):
        """
        Cancelled Samples
        """
        workflow = getToolByName(self, 'portal_workflow')
        l = self.getSamples()
        return [sample for samples in l if
                workflow.getInfoFor(analysis, 'review_state') == 'cancelled']

    def getSamplesPublished(self):
        """
        Published Samples
        """
        workflow = getToolByName(self, 'portal_workflow')
        ars = self.getARs()
        samples = []
        samples_uids = []
        for ar in ars:
            if ar.review_state == 'published':
                # Getting the object now
                sample = ar.getObject().getSample()
                if sample and sample.UID() not in samples_uids:
                    samples.append(sample.UID())
                    samples_uids.append(sample)
        return samples

    def getSamplesOngoing(self):
        """
        Ongoing on Samples
        """
        workflow = getToolByName(self, 'portal_workflow')
        ars = self.getARs()
        states = [
            'verified', 'to_be_sampled', 'scheduled_sampling', 'sampled',
            'to_be_preserved', 'sample_due', 'sample_prep', 'sample_received',
            'to_be_verified', ]
        samples = []
        samples_uids = []
        for ar in ars:
            if ar.review_state in states:
                # Getting the object now
                sample = ar.getObject().getSample()
                if sample and sample.UID() not in samples_uids:
                    samples.append(sample.UID())
                    samples_uids.append(sample)
        return samples

    def getNumberOfSamplesOngoingRatio(self):
        """
        Returns the ratio between NumberOfSamplesOngoing/NumberOfSamples
        """
        result = 0
        if self.getNumberOfSamples() > 0:
            result = self.getNumberOfSamplesOngoing()/self.getNumberOfSamples()
        return result

    security.declarePublic('getARs')

    def getARs(self, analysis_state=None):
        bc = getToolByName(self, 'bika_catalog')
        ars = bc(
            portal_type='AnalysisRequest',
            getPatientUID=self.UID())
        return ars

    def get_clients(self):
        # Only show clients to which we have Manage AR rights.
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

    def get_insurancecompanies(self):
        """
        Return all the registered insurance companies.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        # Void selection
        ret = [('', '')]
        # Other selections
        for ic in bsc(portal_type='InsuranceCompany',
                      inactive_state='active',
                      sort_on='sortable_title'):
            ret.append((ic.UID, ic.Title))
        return DisplayList(ret)

    def getPatientIdentifiersStr(self):
        ids = self.getPatientIdentifiers()
        idsstr = ''
        for idx in ids:
            idsstr += idsstr == '' and idx.get('Identifier', '') or (', ' + idx.get('Identifier', ''))
        return idsstr
        # return self.getSendersPatientID()+" "+self.getSendersCaseID()+" "+self.getSendersSpecimenID()

    def getPatientIdentifiersStrHtml(self):
        ids = self.getPatientIdentifiers()
        idsstr = '<table cellpadding="0" cellspacing="0" border="0" class="patientsidentifiers" style="text-align:left;width: 100%;"><tr><td>'
        for idx in ids:
            idsstr += "<tr><td>" + idx['IdentifierType'] + ':</td><td>' + idx['Identifier'] + "</td></tr>"
        return "</table>" + idsstr

    def getAgeSplitted(self):

        if self.getBirthDate():
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

            if ageday < 0:
                currentmonth -= 1
                if currentmonth < 1:
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
            if agemonth < 0:
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

    def getCountryState(self):
        return self.getField('CountryState').get(self) \
            if self.getField('CountryState').get(self) \
            else self.getPhysicalAddress()

    def getGuarantorID(self):
        """
        If the patient is the guarantor, all the fields related with the guarantor are going to have the same value as
        the current patient fields.
        :return: The guarantor ID (insurance number) from
        """
        return self.getInsuranceNumber() if self.getPatientAsGuarantor() else self.getField('GuarantorID').get(self)

    def getGuarantorSurname(self):
        """
        If the patient is the guarantor, all the fields related with the guarantor are going to have the same value as
        the current patient fields.
        """
        return self.getSurname() if self.getPatientAsGuarantor() else self.getField('GuarantorSurname').get(self)

    def getGuarantorFirstname(self):
        """
        If the patient is the guarantor, all the fields related with the guarantor are going to have the same value as
        the current patient fields.
        """
        return self.getFirstname() if self.getPatientAsGuarantor() else self.getField('GuarantorFirstname').get(self)

    def getGuarantorPostalAddress(self):
        """
        If the patient is the guarantor, all the fields related with the guarantor are going to have the same value as
        the current patient fields.
        """
        return self.getPostalAddress() \
            if self.getPatientAsGuarantor() \
            else self.getField('GuarantorPostalAddress').get(self)

    def getGuarantorBusinessPhone(self):
        """
        If the patient is the guarantor, all the fields related with the guarantor are going to have the same value as
        the current patient fields.
        """
        return self.getBusinessPhone() \
            if self.getPatientAsGuarantor() \
            else self.getField('GuarantorBusinessPhone').get(self)

    def getGuarantorHomePhone(self):
        """
        If the patient is the guarantor, all the fields related with the guarantor are going to have the same value as
        the current patient fields.
        """
        return self.getHomePhone() if self.getPatientAsGuarantor() else self.getField('GuarantorHomePhone').get(self)

    def getGuarantorMobilePhone(self):
        """
        If the patient is the guarantor, all the fields related with the guarantor are going to have the same value as
        the current patient fields.
        """
        return self.getMobilePhone() \
            if self.getPatientAsGuarantor() \
            else self.getField('GuarantorMobilePhone').get(self)

    def getEthnicitiesVocabulary(self, instance=None):
        """
        Obtain all the ethnicities registered in the system and returns them as a list
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title)
                 for c in bsc(portal_type='Ethnicity',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', t(_(''))))
        return DisplayList(items)

    # TODO This function will will be removed on v319
    def getEthnicity(self):
        """
        This function exists because we are changing the construction of ethnicities. Until now, ethnicities options were
        hand-coded but now they are a new content type. So we need to pass all patient's ethnicity values, but to do
        such thing, we need to create new ethnicity types on upgrade step and edit patient ethnicity field to relate them
        with its corresponding ethnicity content type.
        :return:
        """
        return self.getEthnicity_Obj()

    # TODO This function will be removed on v319
    def setEthnicity(self, value):
        self.setEthnicity_Obj(value)

    def getDocuments(self):
        """
        Return all the multifile objects related with the patient
        """
        return self.objectValues('Multifile')

    def SearchableText(self):
        """
        Override searchable text logic based on the requirements.

        This method constructs a text blob which contains all full-text
        searchable text for this content item.
        https://docs.plone.org/develop/plone/searching_and_indexing/indexing.html#full-text-searching
        """

        # Speed up string concatenation ops by using a buffer
        entries = []

        # plain text fields we index from ourself,
        # a list of accessor methods of the class
        plain_text_fields = ("Title", "getFullname", "getId",
                             "getPrimaryReferrerID", "getPrimaryReferrerTitle", "getClientPatientID")

        def read(accessor):
            """
            Call a class accessor method to give a value for certain Archetypes
            field.
            """
            try:
                value = accessor()
            except:
                value = ""

            if value is None:
                value = ""

            return value

        # Concatenate plain text fields as they are
        for f in plain_text_fields:
            accessor = getattr(self, f)
            value = read(accessor)
            entries.append(value)

        # Adding HTML Fields to SearchableText can be uncommented if necessary
        # transforms = getToolByName(self, 'portal_transforms')
        #
        # # Run HTML valued fields through text/plain conversion
        # for f in html_fields:
        #     accessor = getattr(self, f)
        #     value = read(accessor)
        #
        #     if value != "":
        #         stream = transforms.convertTo('text/plain', value, mimetype='text/html')
        #         value = stream.getData()
        #
        #     entries.append(value)

        # Plone accessor methods assume utf-8
        def convertToUTF8(text):
            if type(text) == unicode:
                return text.encode("utf-8")
            return text

        entries = [convertToUTF8(entry) for entry in entries]

        # Concatenate all strings to one text blob
        return " ".join(entries)


# schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(Patient, PROJECTNAME)
