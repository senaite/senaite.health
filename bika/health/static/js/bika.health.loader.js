/**
 * JS responsible of loading the controller classes of health views and forms.
 * Must be embedded to the HTML after the rest of the health's javascripts.
 */
(function( $ ) {
$(document).ready(function(){

    // Correlations between views and js classes to be loaded
    var views = {
        "#batch-base-edit":
            ['BatchEditView',
             'PatientEditView'],

        "#patient-base-edit": 
            ['PatientEditView', ],

        ".template-ar_add #analysisrequest_edit_form":
            ['AnalysisRequestAddView', ]
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