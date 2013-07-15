from Products.CMFCore.utils import getToolByName
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

            addresses = {}
            for add_type in ['Physical', 'Postal']:
                addresses[add_type] = {}
                for key in ['Address', 'City', 'State', 'Zip', 'Country']:
                    addresses[add_type][key] = row.get("%s_%s" % (add_type, key),'')

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
                     EmailAddress = row.get('EmailAddress', ''),
                     BusinessPhone = row.get('BusinessPhone', ''),
                     BusinessFax = row.get('BusinessFax', ''),
                     HomePhone = row.get('HomePhone', ''),
                     MobilePhone = row.get('MobilePhone', ''),
                     PhysicalAddress = addresses['Physical'],
                     PostalAddress = addresses['Postal'],
                     PublicationPreference = row.get('PublicationPreference','').split(","),
                     AttachmentsPermitted = self.to_bool(row.get('AttachmentsPermitted','True'))
                     )
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
            addresses = {}
            for add_type in ['Physical', 'Postal', 'CountryState']:
                addresses[add_type] = {}
                for key in ['Address', 'City', 'State', 'Zip', 'Country']:
                    addresses[add_type][key] = row.get("%s_%s" % (add_type, key),'')

            if addresses['CountryState']['Country'] == '' \
                and addresses['CountryState']['State'] == '':
                addresses['CountryState']['Country'] = addresses['Physical']['Country']
                addresses['CountryState']['State'] = addresses['Physical']['State']

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
                     EmailAddress = row.get('EmailAddress', ''),
                     HomePhone = row.get('HomePhone', ''),
                     MobilePhone = row.get('MobilePhone', ''),
                     PhysicalAddress = addresses['Physical'],
                     PostalAddress = addresses['Postal'],
                     CountryState = addresses['CountryState'],
                     Anonymous = self.to_bool(row.get('Anonymous','False'))
                     )
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
