/**
 * JS responsible of loading the controller classes of health views and forms.
 * Must be embedded to the HTML after the rest of the health's javascripts.
 */
(function( $ ) {
$(document).ready(function(){

    // Correlations between views and js classes to be loaded
    var views = {
        ".template-base_view.portaltype-batch":
            ['BatchViewView'],

        "#batch-base-edit":
            ['BatchEditView',
             'PatientEditView',
             'PatientPublicationPrefsEditView'],

        "#patient-base-edit":
            ['PatientEditView',
             'PatientPublicationPrefsEditView'],

        ".template-ar_add #analysisrequest_edit_form":
            ['AnalysisRequestAddView', ],

        ".template-base_edit.portaltype-bikasetup":
            ['BikaSetupEditView'],

        ".template-base_edit.portaltype-client":
            ['ClientEditView'],
    };

    var loaded = new Array();


    // Instantiate the js objects needed for the current view
    //
    // Whait until the form processing being finished by bika.lims js
    // Just a piece of *shit*, but a 1000ms timeout do the job. Would
    // be great to have a way to know if all the bika.lims.js routines
    // has been finished (also those asyncronous) before triggering
    // the js from extensions.
    setTimeout(function() {
        for (var key in views) {
            if ($(key).length) {
                views[key].forEach(function(js) {
                    if ($.inArray(js, loaded) < 0) {
                        obj = new window[js]();
                        obj.load();
                        loaded.push(js);
                    }
                });
            }
        }
    }, 1000);
});
}(jQuery));
