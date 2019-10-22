/**
 * Controller class for all site views
 */
function HealthSiteView() {

    var that = this;

    that.load = function() {
        if ($('#email_popup').length) {
            $("#email_popup").click(function(event){
                event.preventDefault();
                var dialog = $('<div></div>');
                dialog
                    .load(window.portal_url + "/email_popup",
                        {'uid':$('input[name="email_popup_uid"]').val(),
                         '_authenticator': $('input[name="_authenticator"]').val()}
                    )
                    .dialog({
                        width:450,
                        height:450,
                        closeText: _("Close"),
                        resizable:true,
                        title: "<img src='" + window.portal_url + "/++resource++bika.lims.images/email.png'/>&nbsp;" + $(this).text()
                    });
            });
            if ($('input[name="email_popup_uid"]').attr('autoshow')=='True') {
                $('#email_popup').click();
            }
        }

        /* #HACK
         * https://github.com/bikalabs/Bika-LIMS/issues/928
         * Tricky and foolish stuff to override the hazardous icon in health.
         * Seems that image resources override doesn't work in overrides.zcml
         * (see bika/health/overrides.zcml and bika/health/static/overrides.zcml)
         */
        $("img[src$='bika.lims.images/hazardous.png']").attr('src', window.portal_url + "/++resource++bika.health.images/hazardous.png");
        $("img[src$='bika.lims.images/hazardous_big.png']").attr('src', window.portal_url + "/++resource++bika.health.images/hazardous_big.png");
        $("img[src$='bika.lims.images/client.png']").attr('src', window.portal_url + "/++resource++bika.health.images/client.png");
        $("img[src$='bika.lims.images/client_big.png']").attr('src', window.portal_url + "/++resource++bika.health.images/client_big.png");
        $("img[src$='bika.lims.images/doctor.png']").attr('src', window.portal_url + "/++resource++bika.health.images/doctor.png");
        $("img[src$='bika.lims.images/doctor_big.png']").attr('src', window.portal_url + "/++resource++bika.health.images/doctor_big.png");
        $("img[src$='bika.lims.images/supplyorder.png']").attr('src', window.portal_url + "/++resource++bika.health.images/supplyorder.png");
        $("img[src$='bika.lims.images/supplyorder_big.png']").attr('src', window.portal_url + "/++resource++bika.health.images/supplyorder_big.png");
    }
}
