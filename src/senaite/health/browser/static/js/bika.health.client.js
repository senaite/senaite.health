/**
 * Controller class for BikaSetup edit/creation view
 */
function HealthClientEditView() {

    var that = this;
    that.patientpublicationprefs_section = $("#archetypes-fieldname-PatientPublicationPreferences");
    that.patientattachments_section      = $('#archetypes-fieldname-PatientPublicationAttachmentsPermitted');
    that.patientallowresults_section     = $('#archetypes-fieldname-AllowResultsDistributionToPatients');
    that.defaultpatientpubprefs  = $('#DefaultResultsDistributionToPatients');
    that.patientpublicationprefs = $('#PatientPublicationPreferences');
    that.patientallowresults     = $('#AllowResultsDistributionToPatients');
    that.patientattachments      = $('#PatientPublicationAttachmentsPermitted');
    that.opacity = 0.5;

    /**
     * Entry-point method for BikaSetupEditView
     */
    that.load = function() {

        applyTransitions(false);

        $(that.defaultpatientpubprefs).click(function() {
            applyTransitions(true);
        });

        $(that.patientattachments).click(function() {
            if ($(that.defaultpatientpubprefs).is(':checked')) {
                // Checkbox state mustn't be changed (readonly mode)
                return false;
            }
        });

        $(that.patientallowresults).click(function() {
            if ($(that.defaultpatientpubprefs).is(':checked')) {
                // Checkbox state mustn't be changed (readonly mode)
                return false;
            } else {
                applyTransitions(true);
            }
        });
    }

    /**
     * Apply the transitions to input elements and sections.
     * If the 'Inherit default settings' checkbox is checked, fades the
     * elements of the form out and set them as readonly. Otherwhise, set the
     * fields to editable mode and fades them in.
     * Either if 'Inherit default settings' is checked or unchecked, the
     * visibility of the rest of the elements of the form ('Publication
     * preferences' and 'Publications attachment permitted') depends on the
     * status (checked/unchecked) of the 'AllowResultsDistribution' checkbox.
     * @param fade if false, all the transitions will be done as hide/show. If
     *        true, all the transitions will be done as fadeIn(opacity)/fadeOut
     */
    function applyTransitions(fade) {
        fade = fade == null ? false : fade;

        // Set the input fields to read-only
        isdefault = $(that.defaultpatientpubprefs).is(':checked');
        $(that.patientpublicationprefs).attr('readonly', isdefault);
        $(that.patientattachments).attr('readonly', isdefault);
        $(that.patientallowresults).attr('readonly', isdefault);

        if (isdefault) {
            allow = fillDefaultPatientPrefs();
        }

        if (fade) {
            if (isdefault) {
                $(that.patientallowresults_section).fadeTo("slow", that.opacity);
                if (allow) {
                    $(that.patientpublicationprefs_section).fadeTo("slow", that.opacity);
                    $(that.patientattachments_section).fadeTo("slow", that.opacity);
                } else {
                    $(that.patientpublicationprefs_section).fadeOut("slow");
                    $(that.patientattachments_section).fadeOut("slow");
                }
            } else {
                $(that.patientallowresults_section).fadeTo("slow", 1);
                if ($(that.patientallowresults).is(':checked')) {
                    $(that.patientpublicationprefs_section).fadeTo("slow", 1);
                    $(that.patientattachments_section).fadeTo("slow", 1);
                } else {
                    $(that.patientpublicationprefs_section).fadeOut("slow");
                    $(that.patientattachments_section).fadeOut("slow");
                }
            }
        } else {
            if (isdefault) {
                $(that.patientallowresults_section).fadeTo("fast", that.opacity);
                if (allow) {
                    $(that.patientpublicationprefs_section).fadeTo("fast", that.opacity);
                    $(that.patientattachments_section).fadeTo("fast", that.opacity);
                } else {
                    $(that.patientpublicationprefs_section).hide();
                    $(that.patientattachments_section).hide();
                }
            } else {
                // Custom Patients publication preferences
                if (!$(that.patientallowresults).is(':checked')) {
                    $(that.patientpublicationprefs_section).hide();
                    $(that.patientattachments_section).hide();
                }
            }
        }
    }

    /**
     * Looks for the patient publication preferences from Bika Setup and fill
     * the form with the data retrieved.
     * @returns true if the the client patients are allowed to receive the
     * published results according to Bika Setup settings.
     */
    function fillDefaultPatientPrefs() {
        // Retrieve Patients publication preferences from Bika Setup
        $.ajax({
            url: window.portal_url + "/ajax-bikasetup",
            type: 'POST',
            async: false,
            data: {'_authenticator': $('input[name="_authenticator"]').val(),
                   'id': guid(),
                   'service': 'getDefaultPatientPublicationSettings'
                   },
            dataType: "json",
            success: function(data, textStatus, $XHR){
                if (data['error'] == null) {
                    // Fill the form with default values
                    res = data['result'];
                    $(that.patientallowresults).attr('checked', res['AllowResultsDistributionToPatients']);
                    $(that.patientattachments).attr('checked', res['PatientPublicationAttachmentsPermitted']);
                    $(that.patientpublicationprefs).find('option').each(function() {
                        $(this).attr('selected', jQuery.inArray(this.value, res['PatientPublicationPreferences']) !=-1);
                    });
                } else {
                    console.log(data['error']);
                }
            }
        });
        return $(that.patientallowresults).is(':checked');
    }
}
