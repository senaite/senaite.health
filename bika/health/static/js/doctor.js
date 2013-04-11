(function( $ ) {
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');

    editdoctor_overlay = {
        subtype: 'ajax',
        filter: 'head>*,#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
        formselector: '#doctor-base-edit',
        closeselector: '[name="form.button.cancel"]',
        width:'70%',
        noform:'close',
        config: {
        	onLoad: function() {
        		// manually remove remarks
        		this.getOverlay().find("#archetypes-fieldname-Remarks").remove();
                // Address widget
                $.ajax({
                    url: 'bika_widgets/addresswidget.js',
                    dataType: 'script',
                    async: false
                });
            },
            onClose: function() {
                var Fullname = $("#Firstname").val() + " " + $("#Surname").val();
                if (Fullname.length > 1){
                    $.ajax({
                        url: window.portal_url + "/getDoctorID",
                        type: 'POST',
                        data: {'_authenticator': $('input[name="_authenticator"]').val(),
                                'Fullname': Fullname},
                        dataType: "json",
                        success: function(data, textStatus, $XHR){
                            $("#DoctorID").val(data['DoctorID']);
                            $(".jsDoctorTitle").remove();
                            $("#archetypes-fieldname-DoctorID").append("<span class='jsDoctorTitle'><a class='edit_doctor' href='"+window.portal_url+"/doctors/"+data['DoctorSysID']+"/edit'>"+Fullname+"</a></span>");
                            $('a.edit_doctor').prepOverlay(editdoctor_overlay);
                        }
                    });
                }
            }
        }
    }

    // Add Doctor popup
    $('a.add_doctor').prepOverlay(editdoctor_overlay);

    // Edit Doctor popup
    $('a.edit_doctor').prepOverlay(editdoctor_overlay);

});
}(jQuery));
