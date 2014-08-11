from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode, _createObjectByType
from bika.lims import logger
from bika.lims.exportimport.dataimport import SetupDataSetList as SDL
from bika.lims.exportimport.setupdata import WorksheetImporter
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import ISetupDataSetList
from bika.lims.utils import tmpID
from pkg_resources import resource_filename
from zope.interface import implements


class SetupDataSetList(SDL):

    implements(ISetupDataSetList)

    def __call__(self):
        return SDL.__call__(self, projectname="bika.health")


class Symptoms(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_symptoms
        rows = self.get_rows(3)
        for row in rows:
            _id = folder.invokeFactory('Symptom', id=tmpID())
            obj = folder[_id]
            if row['Title']:
                obj.edit(Code=row.get('Code', ''),
                         title=row['Title'],
                         description=row.get('Description', ''),
                         Gender=row.get('Gender', 'dk'),
                         SeverityAllowed=self.to_bool(row.get('SeverityAllowed', 1)))
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Treatments(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_treatments
        for row in self.get_rows(3):
            obj = _createObjectByType('Treatment', folder, tmpID())
            if row['title']:
                obj.edit(title=row['title'],
                         description=row.get('description', ''),
                         Type=row.get('Type', 'active'),
                         Procedure=row.get('Procedure', ''),
                         Care=row.get('Care', ''),
                         SubjectiveClinicalFindings=row.get('SubjectiveClinicalFindings', ''),
                         ObjectiveClinicalFindings=row.get('ObjectiveClinicalFindings', ''),)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Aetiologic_Agents(WorksheetImporter):

    def get_subtypes(self):
        sheetname = 'Aetiologic Agents Subtypes'
        worksheet = self.workbook.get_sheet_by_name(sheetname)
        if not worksheet:
            return
        subtypes = {}
        rows = self.get_rows(3, worksheet=worksheet)
        for row in rows:
            ae_title = row['aetiologicagent_title']
            if ae_title not in subtypes.keys():
                subtypes[ae_title] = []
            subtypes[ae_title].append({'Subtype': row.get('Subtype', ''),
                                       'SubtypeRemarks': row.get('SubtypeRemarks', '')})
        return subtypes

    def Import(self):
        subtypes = self.get_subtypes()
        folder = self.context.bika_setup.bika_aetiologicagents
        for row in self.get_rows(3):
            obj = _createObjectByType('AetiologicAgent', folder, tmpID())
            if not row['title']:
                continue
            ae_title = row['title']
            ae_subtypes = subtypes.get(ae_title, [])
            obj.edit(title=row['title'],
                     description=row.get('description', ''),
                     AetiologicAgentSubtypes=ae_subtypes)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Case_Syndromic_Classifications(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_casesyndromicclassifications
        for row in self.get_rows(3):
            obj = _createObjectByType('CaseSyndromicClassification', folder, tmpID())
            if row['title']:
                obj.edit(title=row['title'],
                         description=row.get('description', ''),)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Drugs(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_drugs
        for row in self.get_rows(3):
            obj = _createObjectByType('Drug', folder, tmpID())
            if row['title']:
                obj.edit(title=row['title'],
                         description=row.get('description', ''),
                         Category=row.get('Category', ''),
                         Indications=row.get('Indications', ''),
                         Posology=row.get('Posology', ''),
                         SideEffects=row.get('SideEffects', ''),
                         Preservation=row.get('Preservation', ''),)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Drug_Prohibitions(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_drugprohibitions
        for row in self.get_rows(3):
            obj = _createObjectByType('DrugProhibition', folder, tmpID())
            if row['title']:
                obj.edit(title=row['title'],
                         description=row.get('description', ''),)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Identifier_Types(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_identifiertypes
        for row in self.get_rows(3):
            obj = _createObjectByType('IdentifierType', folder, tmpID())
            if row['title']:
                obj.edit(title=row['title'],
                         description=row.get('description', ''),)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Immunizations(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_immunizations
        for row in self.get_rows(3):
            obj = _createObjectByType('Immunization', folder, tmpID())
            if row['title']:
                obj.edit(title=row['title'],
                         description=row.get('description', ''),
                         Form=row.get('Form', 'active'),
                         RelevantFacts=row.get('RelevantFacts', ''),
                         GeographicalDistribution=row.get('GeographicalDistribution', ''),
                         Transmission=row.get('Transmission', ''),
                         Symptoms=row.get('Symptoms', ''),
                         Risk=row.get('Risk', ''),
                         Treatment=row.get('Treatment', ''),
                         Prevention=row.get('Prevention', ''),)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Vaccination_Centers(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_vaccinationcenters
        for row in self.get_rows(3):
            obj = _createObjectByType("VaccinationCenter", folder, tmpID())
            if row['Name']:
                obj.edit(
                    Name=row.get('Name', ''),
                    TaxNumber=row.get('TaxNumber', ''),
                    AccountType=row.get('AccountType', {}),
                    AccountName=row.get('AccountName', {}),
                    AccountNumber=row.get('AccountNumber', ''),
                    BankName=row.get('BankName', ''),
                    BankBranch=row.get('BankBranch', ''),
                )
                self.fill_contactfields(row, obj)
                self.fill_addressfields(row, obj)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Case_Outcomes(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_caseoutcomes
        rows = self.get_rows(3)
        for row in rows:
            if row['title']:
                _id = folder.invokeFactory('CaseOutcome', id=tmpID())
                obj = folder[_id]
                obj.edit(title=row['title'],
                         description=row.get('description', ''))
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Case_Statuses(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_casestatuses
        rows = self.get_rows(3)
        for row in rows:
            if row['title']:
                _id = folder.invokeFactory('CaseStatus', id=tmpID())
                obj = folder[_id]
                obj.edit(title=row['title'],
                         description=row.get('description', ''))
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Diseases(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_symptoms
        rows = self.get_rows(3)
        for row in rows:
            _id = folder.invokeFactory('Disease', id=tmpID())
            obj = folder[_id]
            if row['Title']:
                obj.edit(ICDCode=row.get('ICDCode', ''),
                         title=row['Title'],
                         description=row.get('Description', ''))
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Doctors(WorksheetImporter):

    def Import(self):
        folder = self.context.doctors
        rows = self.get_rows(3)
        for row in rows:
            if not row['Firstname']:
                continue

            _id = folder.invokeFactory('Doctor', id=tmpID())
            obj = folder[_id]
            Fullname = (row['Firstname'] + " " + row.get('Surname', '')).strip()
            obj.edit(title=Fullname,
                     Salutation = row.get('Salutation', ''),
                     Firstname = row.get('Firstname', ''),
                     Surname = row.get('Surname', ''),
                     JobTitle = row.get('JobTitle', ''),
                     Department = row.get('Department', ''),
                     DoctorID = row.get('DoctorID', ''),
                     PublicationPreference = row.get('PublicationPreference','').split(","),
                     AttachmentsPermitted = self.to_bool(row.get('AttachmentsPermitted','True'))
                     )
            self.fill_contactfields(row, obj)
            self.fill_addressfields(row, obj)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Patients(WorksheetImporter):

    def Import(self):
        folder = self.context.patients
        rows = self.get_rows(3)
        for row in rows:
            if not row['Firstname'] or not row['PrimaryReferrer']:
                continue
            pc = getToolByName(self.context, 'portal_catalog')
            client = pc(portal_type='Client', Title=row['PrimaryReferrer'])
            if len(client) == 0:
                raise IndexError("Primary referrer invalid: '%s'" % row['PrimaryReferrer'])

            client = client[0].getObject()
            _id = folder.invokeFactory('Patient', id=tmpID())
            obj = folder[_id]
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            Fullname = (row['Firstname'] + " " + row.get('Surname', '')).strip()
            obj.edit(title=Fullname,
                     ClientPatientID = row.get('ClientPatientID', ''),
                     Salutation = row.get('Salutation', ''),
                     Firstname = row.get('Firstname', ''),
                     Surname = row.get('Surname', ''),
                     PrimaryReferrer = client.UID(),
                     Gender = row.get('Gender', 'dk'),
                     Age = row.get('Age', ''),
                     BirthDate = row.get('BirthDate', ''),
                     BirthDateEstimated =self.to_bool(row.get('BirthDateEstimated','False')),
                     BirthPlace = row.get('BirthPlace', ''),
                     Ethnicity = row.get('Ethnicity', ''),
                     Citizenship =row.get('Citizenship', ''),
                     MothersName = row.get('MothersName', ''),
                     CivilStatus =row.get('CivilStatus', ''),
                     Anonymous = self.to_bool(row.get('Anonymous','False'))
                     )
            self.fill_contactfields(row, obj)
            self.fill_addressfields(row, obj)
            if 'Photo' in row and row['Photo']:
                try:
                    path = resource_filename("bika.lims",
                                             "setupdata/%s/%s" \
                                             % (self.dataset_name, row['Photo']))
                    file_data = open(path, "rb").read()
                    obj.setPhoto(file_data)
                except:
                    logger.error("Unable to load Photo %s"%row['Photo'])

            if 'Feature' in row and row['Feature']:
                try:
                    path = resource_filename("bika.lims",
                                             "setupdata/%s/%s" \
                                             % (self.dataset_name, row['Feature']))
                    file_data = open(path, "rb").read()
                    obj.setFeature(file_data)
                except:
                    logger.error("Unable to load Feature %s"%row['Feature'])

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

class Analysis_Specifications(WorksheetImporter):

    def Import(self):
        s_t = ''
        c_t = 'lab'
        bucket = {}
        pc = getToolByName(self.context, 'portal_catalog')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        # collect up all values into the bucket
        for row in self.get_rows(3):
            c_t = row['Client_title'] if row['Client_title'] else 'lab'
            if c_t not in bucket:
                bucket[c_t] = {}
            s_t = row['SampleType_title'] if row['SampleType_title'] else s_t
            if s_t not in bucket[c_t]:
                bucket[c_t][s_t] = []
            service = bsc(portal_type='AnalysisService', title=row['service'])
            if not service:
                service = bsc(portal_type='AnalysisService',
                              getKeyword=row['service'])
            service = service[0].getObject()
            bucket[c_t][s_t].append({
                'keyword': service.getKeyword(),
                'min': row['min'] if row['min'] else '0',
                'max': row['max'] if row['max'] else '0',
                'minpanic': row['min'] if row['min'] else '0',
                'maxpanic': row['max'] if row['max'] else '0',
                'error': row['error'] if row['error'] else '0'
            })
        # write objects.
        for c_t in bucket:
            if c_t == 'lab':
                folder = self.context.bika_setup.bika_analysisspecs
            else:
                folder = pc(portal_type='Client', title=c_t)[0].getObject()
            for s_t in bucket[c_t]:
                resultsrange = bucket[c_t][s_t]
                sampletype = bsc(portal_type='SampleType', title=s_t)[0]
                _id = folder.invokeFactory('AnalysisSpec', id=tmpID())
                obj = folder[_id]
                obj.edit(
                    title=sampletype.Title,
                    ResultsRange=resultsrange)
                obj.setSampleType(sampletype.UID)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)



from bika.lims.exportimport.setupdata import Setup as BaseSetup

class Setup(BaseSetup):

    def Import(self):
        BaseSetup.Import(self)

        values = {}
        rows = self.get_rows(3)
        for row in rows:
            values[row['Field']] = row['Value']

        self.context.bika_setup.edit(
            EnablePanicAlert=self.to_bool(values.get('EnablePanicAlert', True)),
            EnableAnalysisRemarks=self.to_bool(values.get('EnableAnalysisRemarks', True))
        )
