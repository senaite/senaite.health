// XXX Completely overrides and somewhat duplicates the bika.lims batch.js code
// see jsregistry.xml

(function( $ ) {
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');


    // Load child scripts depending on current view
    js_baseurl = "++resource++bika.health.js/";

    isaraddview = (window.location.href.search('/ar_add') >= 0);
    isfrombatch = (window.location.href.search('batches/') >= 0);

    if (isaraddview && isfrombatch) {
    	/* AR Add View. Automatically fill the Patient, Client and Doctor fields */
    	batchid = window.location.href.split("batches")[1].split("/")[1];
    	$.ajax({
            url: window.portal_url+"/batches/"+batchid+"/getBatchInfo",
            type: 'POST',
            data: {'_authenticator': $('input[name="_authenticator"]').val()},
            dataType: "json",
            success: function(data, textStatus, $XHR){
                for (var col=0; col<parseInt($("#col_count").val()); col++) {
                	$("#ar_"+col+"_Client").val(data['ClientTitle']);
                	$("#ar_"+col+"_Patient").val(data['PatientTitle']);
                	$("#ar_"+col+"_ClientPatientID").val(data['ClientPatientID']);
                	$("#ar_"+col+"_Doctor").val(data['DoctorTitle']);
                	$("#ar_"+col+"_Client_uid").val(data['ClientUID']);
                	$("#ar_"+col+"_Patient_uid").val(data['PatientUID']);
                	$("#ar_"+col+"_Doctor_uid").val(data['DoctorUID']);
                	$("#ar_"+col+"_Client").attr('readonly', true);
                	$("#ar_"+col+"_Patient").attr('readonly', true);
                	$("#ar_"+col+"_Doctor").attr('readonly', true);
                	$("#ar_"+col+"_ClientPatientID").attr('readonly', true);
                }
            }
        });
    }
    
    if ($(".portaltype-batch").length == 0 &&
       window.location.href.search('portal_factory/Batch') == -1){

        $("input[id=BatchID]").after('<a style="border-bottom:none !important;margin-left:.5;"' +
                    ' class="add_batch"' +
                    ' href="'+window.portal_url+'/batches/portal_factory/Batch/new/edit"' +
                    ' rel="#overlay">' +
                    ' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
                ' </a>');
        ajax_url = window.location.href.replace("/ar_add","")
                 + "/getBatches?_authenticator=" + $('input[name="_authenticator"]').val();
        if ($("#ar_0_PatientUID").length > 0) {
            ajax_url = ajax_url + "&PatientUID=" + $("#ar_0_PatientUID").val();
        }
        if ($("#ar_0_ClientUID").length > 0) {
            ajax_url = ajax_url + "&ClientUID=" + $("#ar_0_ClientUID").val();
        }
        $("input[id*=BatchID]").combogrid({
            width: "650px",
            showOn: true,
            colModel: [{'columnName':'BatchUID','hidden':true},
                       {'columnName':'BatchID','width':'16','label':_('Batch ID')},
                       {'columnName':'PatientTitle','width':'28','label':_('Patient')},
                       {'columnName':'DoctorTitle','width':'28','label':_('Doctor')},
                       {'columnName':'ClientTitle','width':'28','label':_('Client')}],
            url: ajax_url,
            select: function( event, ui ) {
                if (window.location.href.search('ar_add') > -1){  // epid ar_add
                    column = $(this).attr('name').split(".")[1];
                    if($('#ar_'+column+'_Patient').length > 0){
                        $('#ar_'+column+'_Patient').val(ui.item.PatientID);
                    }
                    if($('#ar_'+column+'_Doctor').length > 0){
                        $('#ar_'+column+'_Doctor').val(ui.item.DoctorID);
                    }
                    if($('#ar_'+column+'_Client').length > 0){
                        $('#ar_'+column+'_Client').val(ui.item.ClientID);
                    }
                }
                $(this).val(ui.item.BatchID);
                $(this).change();
                return false;
            }
        });

    }

    $('a.add_batch').prepOverlay(
        {
            subtype: 'ajax',
            filter: 'head>*,#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
            formselector: '#batch-base-edit',
            closeselector: '[name="form.button.cancel"]',
            width:'70%',
            noform:'close',
            config: {
                onLoad: function() {
                    // manually remove remarks
                    this.getOverlay().find("#archetypes-fieldname-Remarks").remove();
                },
                onClose: function(){
                    // here is where we'd populate the form controls, if we cared to.
                }
            }
        }
    );

});
}(jQuery));
