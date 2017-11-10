window.bika = window.bika || { lims: {} };
window.bika.health={};
window.jarn.i18n.loadCatalog("bika.health");
var _h = window.jarn.i18n.MessageFactory("bika.health");

/**
 * Dictionary of JS objects to be loaded at runtime.
 * The key is the DOM element to look for in the current page. The
 * values are the JS objects to be loaded if a match is found in the
 * page for the specified key. The loader initializes the JS objects
 * following the order of the dictionary.
 */
window.bika.health.controllers =  {

    "body":
        ['HealthSiteView'],

    ".template-base_view.portaltype-batch":
        ['HealthBatchViewView'],

    "#batch-base-edit":
        ['HealthBatchEditView',
         'HealthPatientEditView',
         'HealthPatientPublicationPrefsEditView',
         'HealthPatientGlobalWidgetEditView'],

    "#patient-base-edit":
        ['HealthPatientEditView',
         'HealthPatientPublicationPrefsEditView'],

    ".template-ar_add #analysisrequest_add_form":
        ['HealthAnalysisRequestAddView'],

    ".template-ar_add #health-standard-ar-add-form":
        ['HealthStandardAnalysisRequestAddView'],

    ".template-base_edit.portaltype-bikasetup":
        ['HealthBikaSetupEditView'],

    ".template-base_edit.portaltype-client":
        ['HealthClientEditView'],

    ".portaltype-patient":
        ['HealthPatientGlobalWidgetEditView'],

    "div.overlay #patient-base-edit":
        ['HealthPatientOverlayHandler'],

    "div.overlay #doctor-base-edit":
        ['HealthDoctorOverlayHandler']

};

window.bika.health.initialized = false;

/**
 * Initializes all bika.health js stuff
 * Add the bika.health controllers inside bikia.lims controllers'
 * dict to be load together.
 */
window.bika.health.initialize = function() {
    if (bika.lims.initialized === true) {
        window.bika.lims.controllers = $.extend(window.bika.lims.controllers, window.bika.health.controllers);
        // We need to force bika.lims.loader to load the bika.health controllers.
        var len = window.bika.lims.initview();
        window.bika.health.initialized = true;
        return len;
    }
    // We should wait after bika.lims has been initialized.
    setTimeout(function() {
        return window.bika.health.initialize();
    }, 500);
};

(function( $ ) {
$(document).ready(function(){

    // Initializes bika.health.
    var length = window.bika.health.initialize();
});
}(jQuery));
