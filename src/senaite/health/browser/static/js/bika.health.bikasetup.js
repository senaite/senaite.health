/**
 * Controller class for BikaSetup edit/creation view
 */
function HealthBikaSetupEditView() {

    var that = this;
    that.patientpublicationprefs = $("#archetypes-fieldname-PatientPublicationPreferences");
    that.patientattachments = $('#archetypes-fieldname-PatientPublicationAttachmentsPermitted');
    that.patientallowresults = $('#AllowResultsDistributionToPatients');

    /**
     * Entry-point method for BikaSetupEditView
     */
    that.load = function() {
        if (!$(that.patientallowresults).is(':checked')) {
            $(that.patientpublicationprefs).hide();
            $(that.patientattachments).hide();
        }
        loadEventHandlers();
    }

    /**
     * Management of events and triggers
     */
    function loadEventHandlers() {
        $(that.patientallowresults).click(function() {
            if ($(this).is(':checked')) {
                $(that.patientpublicationprefs).fadeIn("slow");
                $(that.patientattachments).fadeIn("slow");
            } else {
                $(that.patientpublicationprefs).fadeOut("slow");
                $(that.patientattachments).fadeOut("slow");
            }
        });
    }
}