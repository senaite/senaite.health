(function( $ ) {
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');

    if($(".portaltype-doctor").length == 0 &&
       window.location.href.search('portal_factory/Doctor') == -1){
        $("input[id=Doctor]").after('<a style="border-bottom:none !important;margin-left:.5;"' +
                    ' class="add_doctor"' +
                    ' href="'+window.portal_url+'/doctors/portal_factory/Doctor/new/edit"' +
                    ' rel="#overlay">' +
                    ' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
                ' </a>');
        $("input[id*=Doctor]").combogrid({
            colModel: [{'columnName':'DoctorUID','hidden':true},
                       {'columnName':'DoctorID','width':'20','label':_('Doctor ID')},
                       {'columnName':'Title','width':'80','label':_('Title')}],
            width: "450px",
            showOn: true,
            url: window.portal_url + "/getdoctors?_authenticator=" + $('input[name="_authenticator"]').val(),
            showOn: true,
            select: function( event, ui ) {
                $(this).val(ui.item.DoctorID);
                $(this).change();
                if($(".portaltype-batch").length > 0 && $(".template-base_edit").length > 0) {
                    $(".jsDoctorTitle").remove();
                    $("#archetypes-fieldname-Doctor").append("<span class='jsDoctorTitle'>"+ui.item.Title+"</span>");
                }
                return false;
            }
        });
    }
    // Add Doctor popup
    $('a.add_doctor').prepOverlay(
        {
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
                                $("#Doctor").val(data['DoctorID']);
                                $(".jsDoctorTitle").remove();
                                $("#archetypes-fieldname-DoctorID").append("<span class='jsDoctorTitle'>"+Fullname+"</span>");
                            }
                        });
                    }
                }
            }
	    }
    );

});
}(jQuery));
