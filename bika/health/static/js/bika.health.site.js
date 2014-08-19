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

        // Confirm before resetting client specs to default lab specs
        $("a[href*=set_to_lab_defaults]").click(function(event){
            // always prevent default/
            // url is activated manually from 'Yes' below.
            url = $(this).attr("href");
            event.preventDefault();
            yes = PMF('Yes');
            no = PMF('No');
            var $confirmation = $("<div></div>")
                .html(_("This will remove all existing client analysis specifications "+
                        "and create copies of all lab specifications. "+
                        "Are you sure you want to do this?"))
                .dialog({
                    resizable:false,
                    title: _('Set to lab defaults'),
                    buttons: {
                        yes: function(event){
                            $(this).dialog("close");
                            window.location.href = url;
                        },
                        no: function(event){
                            $(this).dialog("close");
                        }
                    }
                });
        });

        $("input[id=Client]").combogrid({
            colModel: [{'columnName':'ClientUID','hidden':true},
                       {'columnName':'ClientID','width':'20','label':_('Client ID')},
                       {'columnName':'Title','width':'80','label':_('Title')}],
            showOn: true,
            width: '450px',
            url: window.portal_url + "/getClients?_authenticator=" + $('input[name="_authenticator"]').val(),
            showOn: true,
            select: function( event, ui ) {
                $(this).val(ui.item.ClientID);
                $(this).change();
                if($(".portaltype-batch").length > 0 && $(".template-base_edit").length > 0) {
                    $(".jsClientTitle").remove();
                    $("#archetypes-fieldname-Client").append("<span class='jsClientTitle'>"+ui.item.Title+"</span>");
                }
                return false;
            }
        });

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
