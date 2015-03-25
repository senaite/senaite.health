/**
 * Controller class for AnalysisRequest add view for health standard
 */
function HealthStandardAnalysisRequestAddView() {

    var that = this;

    // ------------------------------------------------------------------------
    // PUBLIC ACCESSORS
    // ------------------------------------------------------------------------


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
            cancelPatientCreation();
            // The fields with patient data should be fill out and set them as readonly.
            setDataFromBatch();
        }
        else if (frompatient) {
            // The current AR add View comes from a patient AR folder view.
            // Automatically fill the Client and Patient fields and set them
            // as readonly.
            cancelPatientCreation();
            setDataFromPatient()
        }

        if (!datafilled) {
            // The current AR Add View doesn't come from a batch nor patient .
            // Handle event firing when Patient or ClientPatientID fields change.
            $('[id$="_ClientPatientID"]').bind("selected paste blur change", function () {
               // To load the new patients data
                $('input[id$="_Patient"]').trigger("change");
            });

            $('[id$="_Patient"]').bind("selected paste blur change", function () {
                setPatientData($(this).attr('uid'));
            });

            // Bind the checkbox event.
            $('input#NewPatient').bind("click change", function () {
                hideShowFirstnameSurname();
            });

        };
        hideShowFirstnameSurname();
    };
    // ------------------------------------------------------------------------
    // PRIVATE FUNCTIONS
    // ------------------------------------------------------------------------

    function cancelPatientCreation() {
        /**
         * If the "create a new patient" actions should be canceled, this function hides the specific fields to create
         * a new patient and deactivates the possibility of interact with the checkbox.
         */
        var cb = $('input#NewPatient');
        cb.prop('checked', false);
        // Prevent to be checked
        cb.on('click', function(e){
                e.preventDefault();
                return false;
        });
        cb.hide();
    }

    function hideShowFirstnameSurname(){
        /**
         * Hide/show the fields surname, first name and patient depending on the checkbox state. This function clear
         * all patient data too.
         */
        var cb = $('input#NewPatient');
        if (cb.prop('checked')) {
            $('div#archetypes-fieldname-Patient').hide();
            $('div#archetypes-fieldname-Surname').show();
            $('div#archetypes-fieldname-Firstname').show();

            // Enable and clear all the fields
            $('input#Surname').prop('disabled', false).val('');
            $('input#Firstname').prop('disabled', false).val('');
            $("input#BirthDate").prop('disabled', false).val('');
            $('input#BirthDateEstimated').prop('disabled', false).prop('checked', false);
            $('select#Gender').prop('disabled', false).val('dk');
            $('input#BusinessPhone').prop('disabled', false).val('').attr('uid','');
            $('input#HomePhone').prop('disabled', false).val('');
            $('input#MobilePhone').prop('disabled', false).val('');
            $('input#EmailAddress').prop('disabled', false).val('');
            $('input#ClientPatientID').val('');
        }
        else {

            $('div#archetypes-fieldname-Patient').show();
            $('div#archetypes-fieldname-Surname').hide();
            $('div#archetypes-fieldname-Firstname').hide();

            // Disable and clear all the fields
            $('[id$="_Patient"]').val('').attr('uid','');
            $("input#BirthDate").prop('disabled', true).val('');
            $('input#BirthDateEstimated').prop('disabled', true).prop('checked', false);
            $('select#Gender').prop('disabled', true).val('dk');
            $('input#BusinessPhone').prop('disabled', true).val('');
            $('input#HomePhone').prop('disabled', true).val('');
            $('input#MobilePhone').prop('disabled', true).val('');
            $('input#EmailAddress').prop('disabled', true).val('');
            $('input#ClientPatientID').val('');
        }
    }

    function setDataFromBatch(){
        /**
         * It obtains the patient data. The AR comes from the batch (case).
         */
        var batchid = window.location.href.split("/batches/")[1].split("/")[0];
        $.ajaxSetup({async:false});
        window.bika.lims.jsonapi_read({
            catalog_name:'bika_catalog',
            id:batchid
        }, function(data){
            setPatientData(data.objects[0]['getPatientUID'])
        });
        $.ajaxSetup({async:true});
    }

    function setDataFromPatient(){
        /**
         * It obtains the patient data. The AR comes from the patient.
         */
        var pid = document.referrer.split("/patients/")[1].split("/")[0];
        $.ajaxSetup({async:false});
        window.bika.lims.jsonapi_read({
            catalog_name:'bika_patient_catalog',
            id:pid
        }, function(data){
            setPatientData(data.objects[0])
        });
        $.ajaxSetup({async:true});
    }

    function setPatientData(patientuid){
        /**
         * It fill out the patient data that remains from the bika.analysisrequest.add.js and blocks it.
         * @patientuid The patientuid
         */
        $.ajaxSetup({async:false});
        window.bika.lims.jsonapi_read({
            catalog_name: 'bika_patient_catalog',
            UID: patientuid
        },function(dataobj){
            if (dataobj.objects.length > 0) {
                var data = dataobj.objects[0];
                //$(".dynamic-field-label").remove();
                $("input#BirthDate").val(data['BirthDate']).prop('disabled', true);
                $('input#BirthDateEstimated').prop('checked', data['BirthDateEstimated']).prop('disabled', true);
                $('select#Gender').val(data['Gender']).prop('disabled', true);
                $('input#BusinessPhone').val(data['BusinessPhone']).prop('disabled', true);
                $('input#HomePhone').val(data['HomePhone']).prop('disabled', true);
                $('input#MobilePhone').val(data['MobilePhone']).prop('disabled', true);
                $('input#EmailAddress').val(data['EmailAddress']).prop('disabled', true);

            }
        });
        $.ajaxSetup({async:false});
    }
}
