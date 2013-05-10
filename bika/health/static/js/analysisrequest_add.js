(function( $ ) {
$(document).ready(function(){

	_p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _  = jarn.i18n.MessageFactory('bika.health');
    
    // Load events
    loadEventHandlers();

});
}(jQuery));

function loadEventHandlers() {
	$('[id$="_ClientPatientID"]').bind("selected paste blur", function() {
		colposition = this.id.split("_")[1]
		id = $(this).val()
    	loadPatient(id, colposition);    		
    });
	
	$('[id$="_Patient"]').bind("selected", function() {
		colposition = this.id.split("_")[1]
		uid = $(this).attr('uid');
		loadClientPatientID(uid, colposition);
	});
}

/**
 * Searches a patient using the Patient UID. If found, fill the Patient's
 * input fields from the same AR add column. If no patient found, set the values
 * to Anonymous.
 * @param id Client Patient ID
 * @param colposition AR add column position
 */
function loadPatient(id, colposition) {
	if (id!='') {
		$.ajax({
			url: window.portal_url + "/getpatientinfo",
			type: 'POST',
			data: {'_authenticator': $('input[name="_authenticator"]').val(),
                   'ClientPatientID': id},
        dataType: "json",
        success: function(data, textStatus, $XHR){
        	if (data['PatientUID']!='') {
	        	$("#ar_"+colposition+"_Patient").val(data['PatientFullname']);
	        	$("#ar_"+colposition+"_Patient").attr('uid', data['PatientUID']);
	        	$("#ar_"+colposition+"_Patient_uid").val(data['PatientUID']);
	        	$("#ar_"+colposition+"_Patient").attr("readonly",false);
        	} else {
        		// No patient found. Set anonymous patient
        		$("#ar_"+colposition+"_Patient").val(_('Anonymous'));
	        	$("#ar_"+colposition+"_Patient").attr('uid', 'anonymous');
	        	$("#ar_"+colposition+"_Patient_uid").val('anonymous');
	        	$("#ar_"+colposition+"_Patient").attr("readonly",true);
        	}
        }
		});
	} else {
		// Empty client patient id. Reset patient fields
		$("#ar_"+colposition+"_Patient").val('');
    	$("#ar_"+colposition+"_Patient").attr('uid', '');
    	$("#ar_"+colposition+"_Patient_uid").val('');
    	$("#ar_"+colposition+"_Patient").attr("readonly",false);
	}
}

/**
 * Searches a patient using the Patient UID. If found, fill the Client Patient ID
 * from the same AR add column. If no patient found, set the value to empty.
 * @param uid Patient UID
 * @param colposition AR add column position
 */
function loadClientPatientID(uid, colposition) {
	if (uid!='') {
		$.ajax({
			url: window.portal_url + "/getpatientinfo",
			type: 'POST',
			data: {'_authenticator': $('input[name="_authenticator"]').val(),
                   'PatientUID': uid},
        dataType: "json",
        success: function(data, textStatus, $XHR){
        	$("#ar_"+colposition+"_ClientPatientID").val(data['ClientPatientID']);
        	$("#ar_"+colposition+"_ClientPatientID").attr('uid', uid);
        	$("#ar_"+colposition+"_ClientPatientID_uid").val(uid);
        }
		});
	} else {
		// Empty client patient id. Reset patient fields
		$("#ar_"+colposition+"_ClientPatientID").val('');
    	$("#ar_"+colposition+"_ClientPatientID").attr('uid', '');
    	$("#ar_"+colposition+"_ClientPatientID_uid").val('');
	}
}
