from bika.lims import logger
from bika.lims.exportimport.load_setup_data import LoadSetupData as BaseClass
from bika.lims.idserver import renameAfterCreation
from bika.lims.utils import tmpID
from pkg_resources import resource_listdir, resource_filename, ResourceManager


class LoadSetupData(BaseClass):

    def load_sheets(self, wb):

        # Load bika.lims generic sheets
        BaseClass.load_sheets(self, wb)

        # Load health-specific sheets
        sheets = {}
        self.nr_rows = 0
        for sheetname in wb.get_sheet_names():
            if len(sheetname) > 31:
                print sheetname
            sheets[sheetname] = wb.get_sheet_by_name(sheetname)
            self.nr_rows += sheets[sheetname].get_highest_row()

        if 'Symptoms' in sheets:
            self.load_symptoms(sheets['Symptoms'])
        if 'Aetiologic Agents' in sheets:
            self.lad_patients(sheets['Aetiologic Agents'])
        if 'Case Outcomes' in sheets:
            self.load_caseoutcomes(sheets['Case Outcomes'])
        if 'Case Statuses' in sheets:
            self.load_casestatuses(sheets['Case Statuses'])
        if 'Diseases' in sheets:
            self.load_diseases(sheets['Diseases'])
        if 'Doctors' in sheets:
            self.load_doctors(sheets['Doctors'])
        if 'Drugs' in sheets:
            self.load_drugs(sheets['Drugs'])
        if 'Drug Prohibitions' in sheets:
            self.load_drugprohibitions(sheets['Drug prohibitions'])
        if 'Empidemiological years' in sheets:
            self.load_epidemiologicalyears(sheets['Epidemiological years'])
        if 'Patients' in sheets:
            self.load_patients(sheets['Patients'])
        if 'Immunizations' in sheets:
            self.load_immunizations(sheets['Immunizations'])
        if 'Treatments' in sheets:
            self.load_treatments(sheets['Treatments'])
        if 'Vaccination Centers' in sheets:
            self.load_vaccionationcenters(sheets['Vaccination Centers'])

    def load_casestatuses(self, sheet):
        logger.info("Loading Batch Labels...")
        folder = self.context.bika_setup.bika_casestatuses
        self.casestatuses = {}
        rows = self.get_rows(sheet, 3)
        for row in rows[3:]:
            if row['title']:
                _id = folder.invokeFactory('CaseStatus', id=tmpID())
                obj = folder[_id]
                obj.edit(title=row['title'],
                         description=row.get('description', ''))
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                self.casestatuses[row['title']] = obj

    def load_caseoutcomes(self, sheet):
        logger.info("Loading Case Outcomes...")
        folder = self.context.bika_setup.bika_caseoutcomes
        self.caseoutcomes = {}
        rows = self.get_rows(sheet, 3)
        for row in rows:
            if row['title']:
                _id = folder.invokeFactory('CaseOutcome', id=tmpID())
                obj = folder[_id]
                obj.edit(title=row['title'],
                         description=row.get('description', ''))
                obj.unmarkCreationFlag()
                # renameAfterCreation(obj)
                self.caseoutcomes[row['title']] = obj

    def load_symptoms(self, sheet):
        logger.info("Loading Symptoms...")
        folder = self.context.bika_setup.bika_symptoms
        self.symptoms = {}
        rows = self.get_rows(sheet, 3)
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
                self.symptoms[row['Title']] = obj.UID()
                renameAfterCreation(obj)

    def load_bika_setup(self, sheet):
        BaseClass.load_bika_setup(self, sheet)

        values = {}
        rows = self.get_rows(sheet, 3)
        for row in rows:
            values[row['Field']] = row['Value']

        self.context.bika_setup.edit(
            EnablePanicAlert=self.to_bool(values.get('EnablePanicAlert', True)),
            EnableAnalysisRemarks=self.to_bool(values.get('EnableAnalysisRemarks', True))
        )

    def load_diseases(self, sheet):
        logger.info("Loading Diseases...")
        folder = self.context.bika_setup.bika_symptoms
        self.diseases = {}
        rows = self.get_rows(sheet, 3)
        for row in rows:
            _id = folder.invokeFactory('Disease', id=tmpID())
            obj = folder[_id]
            if row['Title']:
                obj.edit(ICDCode=row.get('ICDCode', ''),
                         title=row['Title'],
                         description=row.get('Description', ''))
                obj.unmarkCreationFlag()
                self.diseases[row['Title']] = obj.UID()
                renameAfterCreation(obj)

    def load_analysis_specifications(self, sheet):
        logger.info("Loading Analysis Specifications...")
        # First we sort the specs by client/sampletype
        #  { Client: { SampleType: { service, min, max, error }... }... }
        all_specs = {}
        rows = self.get_rows(sheet, 3)
        for row in rows:
            client_title = row['Client_title'] or 'lab'
            sampletype_title = row['SampleType_title']
            if client_title not in all_specs:
                all_specs[client_title] = {}
            if sampletype_title not in all_specs[client_title]:
                all_specs[client_title][sampletype_title] = []
            all_specs[client_title][sampletype_title].append({
                'keyword': str(self.services[row['service']].getKeyword()),
                'min': str(row['min']),
                'max': str(row['max']),
                'error': str(row['error']),
                'minpanic': str(row['minpanic']),
                'maxpanic': str(row['maxpanic'])})

        for client, client_specs in all_specs.items():
            if client == 'lab':
                folder = self.context.bika_setup.bika_analysisspecs
            else:
                folder = self.clients[client]
            for sampletype_title, resultsrange in client_specs.items():
                sampletype = self.sampletypes[sampletype_title]
                _id = folder.invokeFactory('AnalysisSpec', id=tmpID())
                obj = folder[_id]
                obj.edit(
                         title=sampletype.Title(),
                         ResultsRange=resultsrange)
                obj.setSampleType(sampletype.UID())
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)

    def load_doctors(self, sheet):
        logger.info("Loading Doctors...")
        self.doctors = {}
        folder = self.context.doctors
        rows = self.get_rows(sheet, 3)
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
            self.doctors[Fullname] = obj

    def load_patients(self, sheet):
        logger.info("Loading Patients...")

        self.patients = {}
        folder = self.context.patients
        rows = self.get_rows(sheet, 3)
        for row in rows:
            if not row['Firstname'] or not row['PrimaryReferrer']:
                continue

            client = self.portal_catalog(portal_type = 'Client',
                                         Title = row['PrimaryReferrer'])
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
            self.patients[Fullname] = obj

    def load_drugs(self, sheet):
        logger.info("Loading Drugs...")
        logger.warn("TODO: load_drugs")

    def load_drugprohibitions(self, sheet):
        logger.info("Loading Drug prohibitions...")
        logger.warn("TODO: load_drugprohibitions")

    def load_epidemiologicalyears(self, sheet):
        logger.info("Loading Epidemiological years...")
        logger.warn("TODO: load_epidemiologicalyears")

    def load_immunizations(self, sheet):
        logger.info("Loading Immunizations...")
        logger.warn("TODO: load_immunizations")

    def load_treatments(self, sheet):
        logger.info("Loading Treatments...")
        logger.warn("TODO: load_treatments")

    def load_vaccinationcenters(self, sheet):
        logger.info("Loading Vaccination Centers...")
        logger.warn("TODO: load_vaccinationcenters")
