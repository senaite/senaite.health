/**
 * JS responsible of loading the controller classes of health views and forms.
 * Must be embedded to the HTML after the rest of the health's javascripts.
 */
(function( $ ) {
$(document).ready(function(){
    
    var views = {
        "#batch-base-edit" : ['BatchEditView', ],
        ".template-ar_add #analysisrequest_edit_form" : ['AnalysisRequestAddView', ]
    };
    
    // Instantiate the js objects needed for the current view
    for (var key in views) {
        if ($(key).length) {
            obj = new window[views[key]]();
            obj.load();
        }
    }
});
}(jQuery));