/**
 * Controller class for AnalysisRequest add view for health standard template
 */
function HealthStandardAnalysisRequestAddView() {
    /**
     * Correct functionality:
     * ======================
     *
     * AR coming from batch:
     * ---------------------
     *  - Patient -> From batch. Fields blocked.
     *  - Guarantor and insurance -> From batch's patient. Fields blocked.
     *  - The save button is going to crate -> an AR
     *
     * AR coming from patient:
     * -----------------------
     *  - Patient -> From patient. Fields blocked.
     *  - Guarantor and insurance -> From the current patient. Fields blocked
     *  - The save button is going to crate -> a case if the checkbox is selected, an AR (related with the case.)
     *
     * AR coming from client:
     * ----------------------
     *  - Patient -> Must be chosen first!
     *  -- If a new patient is being created (NewPatientCheckbox == selected) ->
     *                                                 - Guarantor's + insurance ready to be edited. Fields unblocked.
     *                                                 - Patient fields unblocked.
     *  --- The save button is going to create -> a patient, a case related with the created patient if required, an AR (inside the case)
     *
     *  -- If an old patient is selected (NewPatientCheckbox == unselected) ->
     *                                                 - Guarantor + insurance from selected patient. Fields blocked.
     *                                                 - Patient fields blocked.
     *  --- The save button is going to create -> a case if required, an AR.
     *
     *  How it works?
     *  =============
     *  We can came from three different positions: from a batch, from a patient or from a client.
     *  If we come from a batch, all the client, patient, insurance and doctor's fields will be filled out.
     *  If we come from a patient, the client, patient and insurance will be filled out. We can decide if we want to
     *  create a new batch related with the new analysis request.
     *  If we come from a client(insurance company), we will be able to select an existent patient or create a new one.
     *  In the case we've selected an existing patient, all patient and insurance's fields will be blocked and filled out.
     *  If the checkbox "new patient" is selected all fields will be enabled.
     *
     *  The "GLOBAL" SAVE BUTTON: When the user has filled out all the required fields, he clicks on the save button.
     *  This is NOT the form's button! So after clicking this button, the JS will check if a new patient and a new case
     *  should be created and related each other.
     *  Once these objects' creation (or not) have finished, the data from the patient and the case is copied inside
     *  the analysis request's html form. Then, the javascript clicks on the hidden save button from the form.
     *  Consequently the ajaxForm is gonna create the new Analysis Request.
     *
     */

    var that = this;

    // ------------------------------------------------------------------------
    // PUBLIC FUNCTIONS
    // ------------------------------------------------------------------------

    /**
     * Entry-point method for StandardAnalysisRequestAddView
     */
    this.load = function () {

        var datafilled = false;
        var frombatch = window.location.href.search('/batches/') >= 0;
        var frompatient = document.referrer.search('/patients/') >= 0;

        if (frombatch) {
            // The current AR add View comes from a batch. Automatically fill
            // the Client, Patient and Doctor fields and set them as readonly.
            // Deactivate the option and fields to create a new patient
            datafilled = true;
            var batchid = window.location.href.split("/batches/")[1].split("/")[0];
            cancelPatientCreationCheckBox();
            // The fields with data should be fill out and set them as readonly.
            setDataFromBatch(batchid);
            // Hide and clear the CreateNewCase checkbox
            $('input#CreateNewCase').prop('checked',false).prop('disabled', true)
        }
        else if (frompatient) {
            // The current AR add View comes from a patient's AR folder view.
            // Automatically fill the Client and Patient fields and set them
            // as readonly.
            datafilled = true;
            cancelPatientCreationCheckBox();
            setDataFromPatient()
        }

        if (!datafilled) {
            // The current AR Add View doesn't come from a batch nor patient.
            // Handle event firing when Patient or ClientPatientID fields change.

            // ClientPatientID changed
            $('[id$="_ClientPatientID"]').bind("selected paste blur change", function () {
               // Load the new patients data
                $('input[id$="_Patient"]').trigger("change");
            });

            // PatientFullName changed
            $('[id$="_Patient"]').bind("selected paste blur change", function () {
                // Set the new patient data
                var patientUID = $(this).attr('uid');
                setPatientData(patientUID);
                // Set the new insurance's patient. We can call the function used to fill the insurance data when the
                // AR comes from a batch
                setInsuranceDataFromBatch(patientUID);
            });

            // NewPatient checkbox change
            var np = $('input#NewPatient');
            np.bind("click change", function () {
                // The old patient's data should be uploaded/cleaned
                hideShowFirstnameSurname();
                if (np.prop('checked')) {
                    // If we are creating a new patient we should allow to fill the insurance stuff
                    cleanAndEnableDisableInsuranceData(false);
                }
                else{
                    cleanAndEnableDisableInsuranceData(true);
                }
            });
        }

        // Binding the triggers used on all cases
        $('[id$="_Doctor"]').bind("selected paste blur change", function () {
            setDoctorCode();
        });
        $('input#PatientAsGuarantor').bind("click", function() {
            var cb = $('input#PatientAsGuarantor');
            if (cb.prop('checked')) {
                cleanAndEnableDisableInsuranceData(true);
                cb.prop('disabled', false);
                cb.prop('checked', true);
            }
            else{
                cleanAndEnableDisableInsuranceData(false)
            }
        });

        // Functions to execute at page load
        hideShowFirstnameSurname();
        disableInsuranceData();
        // Unbind previous (from lims) loadAjaxSubmitHandler on submit button.
        $("#analysisrequest_edit_form").ajaxFormUnbind();
        // Bind the new handler
        loadAjaxSubmitHealthHandler();
        $('input#print').bind('click', function(){
            printAnalysisRequest()
        });

    };
    // ------------------------------------------------------------------------
    // PRIVATE FUNCTIONS
    // ------------------------------------------------------------------------

    function setDataFromBatch(batchid){
        /**
         * It obtains the patient's data when the AR comes from the batch (case) view.
         */
        $('#archetypes-fieldname-Batch').remove();
        $.ajaxSetup({async:false});
        // Get batch data
        window.bika.lims.jsonapi_read({
            catalog_name:'bika_catalog',
            id:batchid
        }, function(data){
            // Set patient data
            setPatientData(data.objects[0]['getPatientUID']);
            // Set the doctor's code
            $('input#DoctorsCode').val(data.objects[0]['getDoctorID']).prop('disabled', true);
            // Set the insurance company and block the insurance fields if it's necessary
            setInsuranceDataFromBatch(data.objects[0]['getPatientUID']);
        });
        $.ajaxSetup({async:true});
    }

    function setDataFromPatient(){
        /**
         * It obtains the patient data when the AR comes from the patient view.
         */
        var pid = document.referrer.split("/patients/")[1].split("/")[0];
        $.ajaxSetup({async:false});
        // Get patient data
        window.bika.lims.jsonapi_read({
            catalog_name:'bikahealth_catalog_patient_listing',
            id:pid
        }, function(data){
            setPatientData(data.objects[0]['UID']);
            setInsuranceDataFromPatient(data.objects[0])
        });
        $.ajaxSetup({async:true});
    }

    // Patient template controller ----------------------------------------------------

    function cancelPatientCreationCheckBox() {
        /**
         * If the "create a new patient" actions should be canceled, this function clear the checkbox to create
         * a new patient and deactivates the possibility of interact with the checkbox.
         */
        var cb = $('input#NewPatient');
        cb.prop('disabled', true).prop('checked', false);
    }

    function cleanPatientData(){
        /**
         * Clean all fields used by patient
         */
        $('[id$="_Patient"]').val('').attr('uid','');
        $('input#Surname').val('');
        $('input#Firstname').val('');
        $("input#BirthDate").val('');
        $('input#BirthDateEstimated').prop('checked', false);
        $('select#Gender').val('dk');
        $('input#BusinessPhone').val('').attr('uid','');
        $('input#HomePhone').val('');
        $('input#MobilePhone').val('');
        $('input#EmailAddress').val('');
        $('input#ar_0_ClientPatientID').val('').attr('uid','');
        $('input#PatientID').val('')
    }

    function hideShowFirstnameSurname(){
        /**
         * Hide/show the fields surname, first name and patient depending on the "New patient"'s checkbox state.
         * This function clear all patient data too.
         */
        var cb = $('input#NewPatient');
        if (cb.prop('checked')) {
            $('div#archetypes-fieldname-Patient').hide();
            $('div#PatientID').hide();
            $('div#archetypes-fieldname-Surname').show();
            $('div#archetypes-fieldname-Firstname').show();
            // Hiding the client-patient reference input and showing the simple one used when creating a patient
            $('input#ar_0_ClientPatientID').hide();
            $('input#ClientPatientID').show();

            // Enable and clear all the fields
            $('input#Surname').prop('disabled', false);
            $('input#Firstname').prop('disabled', false);
            $("input#BirthDate").prop('disabled', false);
            $('input#BirthDateEstimated').prop('disabled', false).prop('checked', false);
            $('select#Gender').prop('disabled', false).val('dk');
            $('input#BusinessPhone').prop('disabled', false);
            $('input#HomePhone').prop('disabled', false);
            $('input#MobilePhone').prop('disabled', false);
            $('input#EmailAddress').prop('disabled', false);
            // We should clean the old data
            cleanPatientData()
        }
        else {

            $('div#archetypes-fieldname-Patient').show();
            $('div#PatientID').show();
            $('div#archetypes-fieldname-Surname').hide();
            $('div#archetypes-fieldname-Firstname').hide();
            // Showing the client-patient reference input and hiding the simple one
            $('input#ar_0_ClientPatientID').show();
            $('input#ClientPatientID').hide().val('');

            // Disable and clear all the fields
            $("input#BirthDate").prop('disabled', true);
            $('input#BirthDateEstimated').prop('disabled', true);
            $('select#Gender').prop('disabled', true);
            $('input#BusinessPhone').prop('disabled', true);
            $('input#HomePhone').prop('disabled', true);
            $('input#MobilePhone').prop('disabled', true);
            $('input#EmailAddress').prop('disabled', true);
            //$('input#ar_0_ClientPatientID').prop('disabled', true);
        }
    }

    function setPatientData(patientuid){
        /**
         * It fills out the patient data that remains from the bika.analysisrequest.add.js and blocks it.
         * @patientuid The patient's uid
         */
        if (patientuid == ''){
            // All data patient should be cleaned because no patient has been selected
            cleanPatientData();
            // Disabling the reference input client-patient uid to allow to introduce a patient from here
            $('input#ar_0_ClientPatientID').prop('disabled', false);
        }
        $.ajaxSetup({async:false});
        window.bika.lims.jsonapi_read({
            catalog_name: 'bikahealth_catalog_patient_listing',
            UID: patientuid
        },function(dataobj){
            if (dataobj.objects.length > 0) {
                var data = dataobj.objects[0];
                $("input#BirthDate").val(data['BirthDate']).prop('disabled', true);
                $('input#BirthDateEstimated').prop('checked', data['BirthDateEstimated']).prop('disabled', true);
                $('select#Gender').val(data['Gender']).prop('disabled', true);
                $('input#BusinessPhone').val(data['BusinessPhone']).prop('disabled', true);
                $('input#HomePhone').val(data['HomePhone']).prop('disabled', true);
                $('input#MobilePhone').val(data['MobilePhone']).prop('disabled', true);
                $('input#EmailAddress').val(data['EmailAddress']).prop('disabled', true);
                $('input#ar_0_ClientPatientID').val(data['ClientPatientID']).prop('disabled', true);
                $('input#PatientID').val(data['getPatientID'])
            }
        });
        $.ajaxSetup({async:true});
    }

    // Doctor's template controller ------------------------------------------------

    function setDoctorCode(){
        /**
         * Set the Doctor's code from the selected Referring Doctor.
         */
        var doctoruid = $('[id$="_Doctor"]').attr('uid');
        $.ajaxSetup({async:false});
        window.bika.lims.jsonapi_read({
            catalog_name:'portal_catalog',
            portal_type: 'Doctor',
            UID:doctoruid
        }, function(data){
            $('input#DoctorsCode').val(data.objects[0]['DoctorID']);
        });
        $.ajaxSetup({async:true});
    }

    // Insurance's template controller --------------------------------------------------

    function setInsuranceDataFromBatch(patientuid){
        /**
         * The function checks if the patient is related with an insurance company. In the affirmative case,
         * the insurance fields will be filled out and blocked
         * @patientuid The patient's uid where the function will look for the insurance company.
         */
        if (patientuid == ''){
            // It means that the patient fields have been cleaned of data.
            cleanAndEnableDisableInsuranceData(true);
        }
        else {
            $.ajaxSetup({async: false});
            window.bika.lims.jsonapi_read({
                catalog_name: 'bikahealth_catalog_patient_listing',
                UID: patientuid
            }, function (data) {
                if (data.objects[0]['InsuranceCompany_uid'] != '') {
                    setInsurance(data.objects[0]['InsuranceCompany_uid']);
                }
                // Since data variable stores the patient fields, we can set all guarantor stuff.
                setGuarantor(data.objects[0]);
            });
            $.ajaxSetup({async: true});
        }
    }

    function disableInsuranceData(){
        /**
         * Disable all the fields related with the insurance
         */
        $('input#ar_0_InsuranceCompany').prop('disabled', true);
        $('input#PatientAsGuarantor').prop('disabled', true);
        $('input#GuarantorID').prop('disabled', true);
        $('input#GuarantorSurname').prop('disabled', true);
        $('input#GuarantorFirstname').prop('disabled', true);
        $('select[id="PostalAddress.country"]').prop('disabled', true);
        $('select[id="PostalAddress.state"]').prop('disabled', true);
        $('select[id="PostalAddress.district"]').prop('disabled', true);
        $('input[id="PostalAddress.city"]').prop('disabled', true);
        $('input[id="PostalAddress.zip"]').prop('disabled', true);
        $('textarea[id="PostalAddress.address"]').prop('disabled', true);
        $('input#GuarantorBusinessPhone').prop('disabled', true);
        $('input#GuarantorHomePhone').prop('disabled', true);
        $('input#GuarantorMobilePhone').prop('disabled', true);
    }

    function cleanAndEnableDisableInsuranceData(state){
        /**
         * Clean and enable/disable all the fields related with the insurance
         * @state True/False depending on the disable state
         */
        $('input#ar_0_InsuranceCompany').val('').attr('uid','').prop('disabled', state);
        $('input#PatientAsGuarantor').prop('checked', false).prop('disabled', state);
        $('input#GuarantorID').val('').prop('disabled', state);
        $('input#GuarantorSurname').val('').prop('disabled', state);
        $('input#GuarantorFirstname').val('').prop('disabled', state);
        $('select[id="PostalAddress.country"]')
            .val($('[id="PostalAddress.country"] option[selected="selected"]').val()).prop('disabled', state);
        $('select[id="PostalAddress.state"]').val('').prop('disabled', state);
        $('select[id="PostalAddress.district"]').val('').prop('disabled', state);
        $('input[id="PostalAddress.city"]').val('').prop('disabled', state);
        $('input[id="PostalAddress.zip"]').val('').prop('disabled', state);
        $('textarea[id="PostalAddress.address"]').val('').prop('disabled', state);
        $('input#GuarantorBusinessPhone').val('').prop('disabled', state);
        $('input#GuarantorHomePhone').val('').prop('disabled', state);
        $('input#GuarantorMobilePhone').val('').prop('disabled', state);
    }

    function setInsuranceDataFromPatient(patientdata){
        /**
         * The function checks if the patient is related with an insurance company. In the affirmative case,
         * the insurance fields will be filled out and blocked.
         * @patientuid A dictionary with the patient's data where the function will look for the insurance company.
         */
        // Check if patient is related with an insurance company
        if (patientdata['InsuranceCompany_uid'] != ''){
            setInsurance(patientdata['InsuranceCompany_uid']);
        }
        // Fill out guarantor's fields
        setGuarantor(patientdata);
    }

    function setInsurance(insuranceuid){
        /**
         * This function fill out the insurance field and block it.
         * @insuranceuid The insurance company UID
         */
        if (insuranceuid != undefined) {
            $.ajaxSetup({async: false});
            window.bika.lims.jsonapi_read({
                catalog_name: 'bika_setup_catalog',
                content_type: 'InsuranceCompany',
                UID: insuranceuid
            }, function (dataobj) {
                var data = dataobj.objects[0];
                $('input#ar_0_InsuranceCompany').val(data['Title']).attr('uid', data['UID']).prop('disabled', true);
            });
            $.ajaxSetup({async: true});
        }
    }

    function setGuarantor(patientdata) {
        /**
         * It fills out all guarantor's fields.
         * @patientdata It's a dictionary with the patient's data
         */
        // The AR comes from batch or patients view
        $('input#PatientAsGuarantor').prop('checked', patientdata['PatientAsGuarantor']).prop('disabled', true);
        $('input#GuarantorID').val(patientdata['GuarantorID']).prop('disabled', true);
        $('input#GuarantorSurname').val(patientdata['GuarantorSurname']).prop('disabled', true);
        $('input#GuarantorFirstname').val(patientdata['GuarantorFirstname']).prop('disabled', true);
        $('select[id="PostalAddress.country"]').val(patientdata['PostalAddress']['country']).prop('disabled', true);
        $('select[id="PostalAddress.state"]').val(patientdata['PostalAddress']['state']).prop('disabled', true);
        $('select[id="PostalAddress.district"]').val(patientdata['PostalAddress']['district']).prop('disabled', true);
        $('input[id="PostalAddress.city"]').val(patientdata['PostalAddress']['city']).prop('disabled', true);
        $('input[id="PostalAddress.zip"]').val(patientdata['PostalAddress']['zip']).prop('disabled', true);
        $('textarea[id="PostalAddress.address"]').val(patientdata['PostalAddress']['address']).prop('disabled', true);
        $('input#GuarantorBusinessPhone').val(patientdata['GuarantorBusinessPhone']).prop('disabled', true);
        $('input#GuarantorHomePhone').val(patientdata['GuarantorHomePhone']).prop('disabled', true);
        $('input#GuarantorMobilePhone').val(patientdata['GuarantorMobilePhone']).prop('disabled', true);
    }

    // Defining the health submit handler -----------------------------------------------------

    function loadAjaxSubmitHealthHandler(){
        /**
         * This functions builds the options to create the objects and binds the needed functions to create the objects
         * after submit.
         * Since the different objects definitions are split into different forms, on the form's submit we have to create
         * every object (if it's necessary) from every form, and copy its data into the analysis request's form to create
         * the analysis request with all the recently created objects.
         */
        $('input#global_save_button').bind('click', function(){
            // If the Analysis Request comes form a case (batch), the fields ClientPatientID, Doctor and Patient should
            // be copied from their forms to the Analysis Request form.
            if ($('input#NewPatient').prop('checked')){
                // A patient should be created
                createPatient();
            }
            if ($('input#CreateNewCase').prop('checked')){
                // Creating a case
                createCase();
            }
            // Coping the patient from the patient's creation form to the analysis request's creation form
            $("form#analysisrequest_patient_edit_form #archetypes-fieldname-Patient")
                .clone().appendTo("form#analysisrequest_edit_form").hide();
            // Coping the doctor
            $("div#archetypes-fieldname-Doctor")
                .clone().appendTo("form#analysisrequest_edit_form").hide();
            // Coping the Client-Patient-ID
            $("form#analysisrequest_patient_edit_form #archetypes-fieldname-ClientPatientID")
                .clone().appendTo("form#analysisrequest_edit_form").hide();

            var options = createAR();
            $("#analysisrequest_edit_form").ajaxForm(options);
            // Click on analysis request form to trigger the AR creation
            $('form#analysisrequest_edit_form input[name="save_button"]').click();
        });
    }

    // Creating an AR ---------------------------------------------------------------------

    function createAR(){
        /**
         * This function creates an Analysis Request.
         */
        var options = {
            url: window.location.href.split("/portal_factory")[0] + "/analysisrequest_submit",
            dataType: "json",
            data: {"_authenticator": $("input[name='_authenticator']").val()},
            beforeSubmit: function() {
                $("input[class~='context']").prop("disabled",true);
            },
            success: function(responseText) {
                var destination;
                if(responseText.success !== undefined){
                    if(responseText.stickers !== undefined){
                        destination = window.location.href
                            .split("/portal_factory")[0];
                        var ars = responseText.stickers;
                        var template = responseText.stickertemplate;
                        var q = "/sticker?template="+template+"&items=";
                        q = q + ars.join(",");
                        window.location.replace(destination+q);
                    } else {
                        destination = window.location.href
                            .split("/portal_factory")[0];
                        window.location.replace(destination);
                    }
                } else {
                    var msg = "";
                    for(var error in responseText.errors){
                        var x = error.split(".");
                        var e;
                        if (x.length == 2){
                            e = x[1] + ", Column " + (+x[0]) + ": ";
                        } else {
                            e = "";
                        }
                        msg = msg + e + responseText.errors[error] + "<br/>";
                    }
                    window.bika.lims.portalMessage(msg);
                    window.scroll(0,0);
                    $("input[class~='context']").prop("disabled", false);
                }
            },
            error: function(XMLHttpRequest, statusText) {
                window.bika.lims.portalMessage(statusText);
                window.scroll(0,0);
                $("input[class~='context']").prop("disabled", false);
            }
        };
        return options;
    }
    // Creating a Patient ----------------------------------------------------------------

    function createPatient(){
        /**
         * This function creates a patient via ajax and jsonapi from the data introduced in the form.
         */
        var request_data = {
            obj_path: '/Plone/patients',
            obj_type: 'Patient',
            ClientPatientID: $('input#ClientPatientID').val(),
            Surname: $('#Surname').val(),
            Firstname: $('#Firstname').val(),
            BirthDate: $('#BirthDate').val(),
            BirthDateEstimated: $('#BirthDateEstimated').prop('checked'),
            Gender: $('#Gender').val(),
            HomePhone: $('#HomePhone').val(),
            MobilePhone: $('#MobilePhone').val(),
            BusinessPhone: $('#BusinessPhone').val(),
            EmailAddress: $('#EmailAddress').val(),
            PatientAsGuarantor: $('#PatientAsGuarantor').prop('checked'),
            PrimaryReferrer: "portal_type:Client|UID:" + $('input#ar_0_Client_uid').val()
        };
        if (!request_data['PatientAsGuarantor']){
            var request_data_ext = {
                GuarantorID: $('#GuarantorID').val(),
                GuarantorFirstname: $('#GuarantorFirstname').val(),
                GuarantorSurname: $('#GuarantorSurname').val(),
                PostalAddress: $.toJSON({country:$('[id="PostalAddress.country"]').val(), state:$('[id="PostalAddress.state"]').val(),
                                city:$('[id="PostalAddress.city"]').val(), address:$('[id="PostalAddress.address"]').val(),
                                zip:$('[id="PostalAddress.zip"]').val()}),
                GuarantorHomePhone: $('#GuarantorHomePhone').val(),
                GuarantorMobilePhone: $('#GuarantorMobilePhone').val(),
                GuarantorBusinessPhone: $('#GuarantorBusinessPhone').val()
            };
            $.extend(request_data,request_data_ext)
        }
        $.ajaxSetup({async: false});
        $.ajax({
            type: "POST",
            dataType: "json",
            url: window.portal_url + "/@@API/create",
            data: request_data,
            success: function(data){
                // Getting the case's uid
                window.bika.lims.jsonapi_read({
                    catalog_name: 'bikahealth_catalog_patient_listing',
                    content_type: 'Patient',
                    id: data['obj_id']
                }, function (dataobj) {
                    // After creating the new patient, we should fill the "existing patient"'s input. When we are
                    // creating the analysis request, this input is going to be cloned to the analysis request form, and
                    // consequently, the AR and the patient will be related.
                    $('input#ar_0_Patient').attr('uid', dataobj.objects[0]['UID']);
                    $('input#ar_0_Patient_uid').val(dataobj.objects[0]['UID']);
                    $('input#ar_0_Patient').val(dataobj.objects[0]['title'])
                });
            },
            error: function(XMLHttpRequest, statusText) {
                window.bika.lims.portalMessage(statusText);
                window.scroll(0,0);
                $("input[class~='context']").prop("disabled", false);
            }
        });
        $.ajaxSetup({async: true});
    }

    // Creating a batch (case) ------------------------------------------------------------

    function createCase(){
        /**
         * This function reads the data from the doctor and the patient, and consequently creates a case.
         * Finally it fills the case's input inside the analysis request form.
         */
        var patientuid = $('input#ar_0_Patient').attr('uid');
        var doctoruid = $('input#ar_0_Doctor').attr('uid');
        var clientuid = $('input#ar_0_Client_uid').val();
        var request_data = {
            obj_path: '/Plone/batches',
            obj_type: 'Batch',
            Patient: "catalog_name:bikahealth_catalog_patient_listing|portal_type:Patient|UID:" + patientuid,
            Doctor:"portal_type:Doctor|UID:" + doctoruid,
            Client:"portal_type:Client|UID:" + clientuid
        };
        $.ajaxSetup({async: false});
        $.ajax({
            type: "POST",
            dataType: "json",
            url: window.portal_url + "/@@API/create",
            data: request_data,
            success: function(data){
                // To obtain the case's uid
                window.bika.lims.jsonapi_read({
                    catalog_name: 'bika_catalog',
                    content_type: 'Batch',
                    id: data['obj_id']
                }, function (dataobj) {
                    // Writing the case's uid inside the analysis request creation's form. Thus when the analysis
                    // request form submits, it will catch the case's uid and create it.
                    $('form#analysisrequest_edit_form input#ar_0_Batch').attr('uid', dataobj.objects[0]['UID']);
                    $('form#analysisrequest_edit_form input#ar_0_Batch_uid').val(dataobj.objects[0]['UID']);
                });
                // The case's input also needs their id.
                $('form#analysisrequest_edit_form input#ar_0_Batch').val(data['obj_id']);
            },
            error: function(XMLHttpRequest, statusText) {
                window.bika.lims.portalMessage(statusText);
                window.scroll(0,0);
                $("input[class~='context']").prop("disabled", false);
            }
        });
        $.ajaxSetup({async: true});
    }

    <!-- Printing the Analysis Request -->
    function printAnalysisRequest(){
        /**
         * This function triggers the browser's print-page option.
         */
        window.print()
    }
}
