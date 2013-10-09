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

    // Instantiate the js objects needed for the current view
    var loaded = new Array();
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
});
}(jQuery));