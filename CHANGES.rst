Changelog
=========

1.1.2 (unreleased)
------------------

**Added**


**Changed**


**Removed**


**Fixed**


**Security**


1.1.1 (2018-04-07)
------------------

**Added**

- #56 Option for making Client Patient IDs unique
- #63 Display Doctor column in Analysis Requests listings

**Changed**

- #48 After Patient creation, redirect to Patient's Analysis Requests view

**Fixed**

- #64 Samples not filtered in Doctor's samples view
- #52 Date Reported is missing in reports
- #52 Date Collected is missing in reports
- #45 ConfigurationConflictError in "The workflow actions menu"
- #49 Default publication preference for Patients in Clients vocabulary error
- #44 Traceback on "copy to new" Analysis Request


1.1.0 (2018-01-26)
------------------

**Changed**

- #33 #37 bika.lims to senaite.core distribution
- #39 Improved performance for Patient listings

**Fixed**

- #39 Traceback on Patients when current user has Client role but is LabContact
- #36 Using parameter "vocabulary" wasn't working in bika_setup
- #35 Analysis Request View error when the page redirects the user
- #44 Traceback on "copy to new" Analysis Request


1.0.0 (2017-11-10)
------------------

**Added**

- #30 Allow Client contacts to create patients
- #28 Asynchronous creation of Analysis Requests
- #18 Wildcards on searching in Patients lists
- #13 Added 'meta_type' column in Patient catalog
- #7 New Analysis Request Add form outside client and patient

**Changed**

- #27 Remove health's bika_analysis_workflow.csv and use bika.lims' one instead
- #21 Replacement of FileField by BlobField
- #20 SearchableText index moved to the base dictionary in LIMS
- #15 Base catalog template definition for indexes and metadata
- #9 Worksheet performance improvements
- #6 Added specific catalog for Analysis object types
- #4 Migration of filter bar definition for ARs and samples, from health to lims
- #2 Added specific catalog for Analysis Request object types

**Fixed**

- #32 Can't search using Client Patient ID in patient listing
- #31 Can't search using Client Patient ID in batches listing
- #29 AttributeError: 'module' object has no attribute 'ViewPatients'
- #26 CatalogError: unknown sort_on index (Patient)
- #25 AttributeError on publish: 'NoneType' object has no attribute 'bika_setup'
- #24 CatalogError in Patients folder view: unknown sort_on index (Title)
- #23 UnboundLocalError in Samples view: local variable 'ar' referenced before assignment
- #22 Worksheets not displaying analyses
- #19 Batch View. CatalogError: Unknown sort_on index (BatchID)
- #17 Unable to create specifications with min/max panic levels
- #16 ValueError while saving a clinical case: 'BatchID' is not in list
- #14 Analysis Request Submit (AJAX call). KeyError: 'state'
- #12 CatalogError: Unknown sort_on index (created) in view.get_sections() from dashboard
- #11 Error on install: unexpected keyword argument 'catalog_extensions'
- #11 Error on install: Can't pickle BikaPatientCatalog
- #10 Sort on Patient not working in lists (Analysis Requests, Samples and Patients)
- #3 Bug during getPatientInfo from AR add view


3.2.0.1503-e5a0358 (2016-03-18)
-------------------------------
- Updated to work with BikaLIMS 3.2
- HEALTH-503: Validation of Date of birth
- HEALTH-497: Hide Doctor field on EID Case Form
- HEALTH-357: UI. Post Patient Create landing page
- HEALTH-361: VL Cases
- HEALTH-413: Dashboard not showing
- HEALTH-402: In Analysis Request Add form, contact doesn't get selected


3.1.8 (2015-11-03)
------------------

- HEALTH-301: Use newer version of Health flow diagram in next release
- HEALTH-281: Error in Bika Setup › Insurance Companies > Invoices
- HEALTH-305: Having invoices
- HEALTH-370: Worksheet architecture has changed in LIMS
- HEALTH-269: Analysis Request Add compatibility with LIMS 3.1.9
- HEALTH-273: Error upgrading to 317
- HEALTH-270: Error while importing patient with "yearinprefix" disabled
- HEALTH-271: Analysis request invoice view broken
- HEALTH-266: View error on invoice from analysis request
- HEALTH-258: Add "File attachment" on Patient


3.1.7 (2015-06-09)
------------------

- HEALTH-282: Error loading Add Analysis request
- HEALTH-245: Set-up data load. Patient ID conversion, alternatives
- HEALTH-227: Converting Patient IDs before import
- HEALTH-228: Load Setup data bugs
- HEALTH-140: AR Create per path lab standard form
- HEALTH-251: Add guarantor details in insurance companies


3.1.6 (2015-02-27)
------------------

- HEALTH-223: When you are adding a doctor through an overlay (add doctor button in cases), the address widgets don't work properly.
- HEALTH-215: Correct Navigation tree order
- HEALTH-191: Client Contact permissions
- HEALTH-137: Medical Insurance for Patients. Alternative invoice workflow
- HEALTH-204: Doctor Samples view broken
- HEALTH-200: Additional picklists don't work when creating Patients directly from the Case's view
- HEALTH-136: [+ Add] Patient button on AR Create form.
- HEALTH-179: "Copy to new" button in AR, doesn't copy the selected data.
- HEALTH-197: Health's results report error.
- HEALTH-204: Batch.samples error loading page
- HEALTH-177: Past Medical History and Drug History's end date selection error.
- HEALTH-178: Past Medical History, Travell History and Immunization History data: Impossible to remove the last set of data.
- HEALTH-208: Incompatibilty with new Bika LIMS' add site templates
- HEALTH-197: Health's results report error
- HEALTH-189: Patient Edit page: After define a country, it is not saved.
- HEALTH-184: Add Case: Patient Age at Case Onset Date doesn't get filled after introduce the Onset Date.


3.1.5 (2014-10-10)
------------------

- HEALTH-176: Cannot choose a drug from the dropdown list on Patient->allergies
- HEALTH-174: Unable to add an AR to a Case (missing Client)
- HEALTH-163: Cannot be chosen Immunisation items from dropdown list.
- HEALTH-162: Cannot choose Drug Prohibition Explanation
- HEALTH-169: Analyst can't see Samples site, Admin can.
- HEALTH-168: Diagnosis ICD widget does not complete from Code, Description
- HEALTH-161: In Add Patient, after introducing the Birth Date, the patient's age don't get filled automatically.
- HEALTH-157: Patient field is missing in AR add views
- HEALTH-150: Compatibility with the new JS loader machinery
- HEALTH-164: Editing a patient, location not have to be important on Travel History field
- HEALTH-166: "Patient Age at Case Onset Date" in Add Case cannot be filled
- HEALTH-172: Anything is displayed on drugs list
- HEALTH-173: ImmunizationHistory cannot save data
- HEALTH-149: Compatibility with the new Bika LIMS reporting subsystem
- HEALTH-152: Upgrade the test data worksheet
- HEALTH-145: Health icons not used. And 1 more
- HEALTH-152: Upgrade the test data worksheet

- Plus Bika-LIMS 3.1.5: http://git.io/ogjDuQ


3.1.2.1 (2014-08-05)
--------------------

- HEALTH-144: Set up data: Identifier Types NameError: global name '_id' is not defined
- HEALTH-143: Can not create site


3.1.2 (2014-07-25)
------------------

- HEALTH-104: Health Setup data failures
- HEALTH-28: Health load setup data. Drugs and Treatments did not import
- HEALTH-105: Case syndromic classifications site eror in setup
- HEALTH-93: AR. Updating Info portion
- HEALTH-27: AR Create. Copying Patient fields across does not autocomplete corresponding Name or ID

- Plus Bika-LIMS 3.1.2 and 3.1.3: http://git.io/MWb4dQ


3.1.1 (2014-07-11)
------------------

- HEALTH-122: Client contact cannot open Client page/AR page blank
- HEALTH-92: Display Patients tab inside Referral Institution (Client)
- HEALTH-109: Manually adding symptoms saving but remaining on the same page
- HEALTH-124: Client contact can access doctors and patients of other clients
- HEALTH-121: Client contact gets Insufficient Privileges upon login
- HEALTH-133: Case creation: Basal body temperature fields accepting values way out of range
- HEALTH-106: Mimetype text/plain is not allowed in Drug edit view
- HEALTH-73: Current and Historic results in PDF sorted in the same order
- HEALTH-61: Sort Symptoms table on gender
- HEALTH-23: No drugs listed in Drugs folder
- Hyperlinks to Analysis Requests in Patient's Historic Results


3.1 Naringenin (2014-06-04)
---------------------------

- Inherits all features from Bika LIMS release/3.1
- Customisations towards CLIA compliance
- Incorrect published results invalidation workflow
- Regulatory Inspector role
- Tighter Patient privacy restrictions
- Life Threat Alert
- Public Results specifications
- Results reports inclusion of relevant QC results
- Patient results history graphs
- Simplified Clinical Case sections for Signs and Symptoms, Patient Condition
- Stream-lined anonymous Patient workflow


0.1 (2012-12-31)
----------------

- Create separate product from the Bika-LIMS/health branch.
