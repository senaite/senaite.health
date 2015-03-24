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
        datafilled = false;
        frombatch = window.location.href.search('/batches/') >= 0;
        frompatient = document.referrer.search('/patients/') >= 0;

        if (frombatch) {
            // The current AR add View comes from a batch. Automatically fill
            // the Client, Patient and Doctor fields and set them as readonly.

        } else if (frompatient) {
            // The current AR add View comes from a patient AR folder view.
            // Automatically fill the Client and Patient fields and set them
            // as readonly.
        }

        if (!datafilled) {
            // The current AR Add View doesn't come from a batch nor patient or
            // data autofilling failed. Handle event firing when Patient or
            // ClientPatientID fields change.


            $('[id$="_Patient"]').bind("selected paste blur change", function () {
                colposition = $(this).closest('td').attr('column');
                uid = $("#" + this.id + "_uid").val();
            });

            // When the user selects an earlier sample (from storage say) and creates a
            // secondary AR for it, the Patient field should also be looked up and
            // uneditable.
            // See https://github.com/bikalabs/bika.health/issues/100
            $('[id$="_Sample"]').bind("selected paste blur", function () {
                colposition = $(this).closest('td').attr('column');
                uid = $("#" + this.id + "_uid").val();
            });

            // The Batch, Patient and PatientCID combos must only show the
            // records from the current client
        }


        // Check if the current selected client has contacts. If client has no
        // contacts, prevent from saving the AR and inform the user
    };

    // ------------------------------------------------------------------------
    // PRIVATE FUNCTIONS
    // ------------------------------------------------------------------------


    // New patient checkbox and needed fields to create one should be hidden
    //$('input#NewPatient').prop('checked', false);
    //$("#archetypes-fieldname-NewPatient").attr.hide();

}
