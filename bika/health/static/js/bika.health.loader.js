'use strict';
window.bika = window.bika || { lims: {} };
window.bika['health']={};
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
         'HealthPatientPublicationPrefsEditView'],

    "#patient-base-edit":
        ['HealthPatientEditView',
         'HealthPatientPublicationPrefsEditView'],

    ".template-ar_add #analysisrequest_edit_form":
        ['HealthAnalysisRequestAddView', ],

    ".template-base_edit.portaltype-bikasetup":
        ['HealthBikaSetupEditView'],

    ".template-base_edit.portaltype-client":
        ['HealthClientEditView'],

};

/**
 * Initializes only the js controllers needed for the current view.
 * Initializes the JS objects from the controllers dictionary for which
 * there is at least one match with the dict key. The JS objects are
 * loaded in the same order as defined in the controllers dict.
 */
window.bika.health.initview = function() {
    var loaded = new Array();
    var controllers = window.bika.health.controllers;
    for (var key in controllers) {
        if ($(key).length) {
            controllers[key].forEach(function(js) {
                if ($.inArray(js, loaded) < 0) {
                    console.debug('[bika.health.loader] Loading '+js);
                    try {
                        obj = new window[js]();
                        obj.load();
                        // Register the object for further access
                        window.bika.health[js]=obj;
                        loaded.push(js);
                    } catch (e) {
                       // statements to handle any exceptions
                       var msg = '[bika.health.loader] Unable to load '+js+": "+ e.message +"\n"+e.stack;
                       console.warn(msg);
                       window.bika.lims.error(msg);
                    }
                }
            });
        }
    }
    return loaded.length;
};

window.bika.health.initialized = false;

/**
 * Initializes all bika.health js stuff
 */
window.bika.health.initialize = function() {
    if (bika.lims.initialized == true) {
        return window.bika.health.initview();
    }
    // We should wait after bika.lims being initialized
    setTimeout(function() {
        return window.bika.health.initialize();
    }, 500);
};

(function( $ ) {
$(document).ready(function(){

    // Initializes bika.health
    var length = window.bika.health.initialize();
    window.bika.health.initialized = true;

});
}(jQuery));
