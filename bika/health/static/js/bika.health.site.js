/**
 * Controller class for all site views
 */
function HealthSiteView() {

    var that = this;

    that.load = function() {
        /* #HACK
         * https://github.com/bikalabs/Bika-LIMS/issues/928
         * Tricky and foolish stuff to override the hazardous icon in health.
         * Seems that image resources override doesn't work in overrides.zcml
         * (see bika/health/overrides.zcml and bika/health/static/overrides.zcml)
         */
        $("img[src$='bika.lims.images/hazardous.png']").attr('src', window.portal_url + "/++resource++bika.health.images/hazardous.png");
        $("img[src$='bika.lims.images/hazardous_big.png']").attr('src', window.portal_url + "/++resource++bika.health.images/hazardous_big.png");
        $("img[src$='bika.lims.images/doctor.png']").attr('src', window.portal_url + "/++resource++bika.health.images/doctor.png");
        $("img[src$='bika.lims.images/doctor_big.png']").attr('src', window.portal_url + "/++resource++bika.health.images/doctor_big.png");
    }
}
