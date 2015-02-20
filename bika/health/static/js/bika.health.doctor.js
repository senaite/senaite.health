'use strict;'

/**
 * Controller class for Doctor edit/creation view
 */

function HealthDoctorOverlayHandler() {
    /**
     * Doctor's overlay edit view Handler. Used by add buttons to
     * manage the behaviour of the overlay and load some widgets' JS.
     */
    var that = this;

    // Needed for bika.lims.loader to register the object at runtime
    that.load = function() {};

    /**
     * Event fired on overlay.onLoad()
     * Load the addresswidget js controller.
     */
    that.onLoad = function() {
        // Address widget
        $.ajax({
            url: 'bika_widgets/addresswidget.js',
            dataType: 'script',
            async: false
        });
    }
}
