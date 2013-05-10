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
	$('[id$="_ClientPatientID"]').live('change', function() {
    	colposition = getColPosition(this.attr('name'));
    	clientpid = this.val()
    	if (colposition > -1) {
        	loadPatient(clientpid, colposition);    		
    	}
    });
}

/**
 * Returns the AR add column position in which the field is located. If no
 * column position is found, returns -1
 * @param fieldname
 * @returns the AR add column position
 */
function getColPosition(fieldname) {
	var re = new RegExp("^ar_([\d+])_");
	var m = re.exec(fieldname);
	if (m != null && m.length==2) {
		return m[1];
	}
	return -1;
}

/**
 * Searches a patient using the Client Patient ID. If found, fill the Patient's
 * input fields from the same AR add column. If no patient found, set the values
 * to Anonymous.
 * @param clientpid Client Patient ID
 * @param colposition AR add column position
 */
function loadPatient(clientpid, colposition) {
	if (clientpid!='') {
		$.ajax({
			url: window.portal_url + "/getpatientinfo",
			type: 'POST',
			data: {'_authenticator': $('input[name="_authenticator"]').val(),
                   'ClientPatientID': clientPID},
        dataType: "json",
        success: function(data, textStatus, $XHR){
        	if (data['PatientUID']!='') {
	        	$("#ar_"+colposition+"_Patient").val(data['PatientFullname']);
	        	$("#ar_"+colposition+"_Patient").attr('uid', data['PatientUID']);
	        	$("#ar_"+colposition+"_Patient_uid").val(data['PatientUID']);
        	} else {
        		// No patient found. Set anonymous patient
        		$("#ar_"+colposition+"_Patient").val(_('Anonymous'));
	        	$("#ar_"+colposition+"_Patient").attr('uid', 'anonymous');
	        	$("#ar_"+colposition+"_Patient_uid").val('anonymous');
        	}
        }
		});
	} else {
		// Empty client patient id. Reset patient fields
		$("#ar_"+colposition+"_Patient").val('');
    	$("#ar_"+colposition+"_Patient").attr('uid', '');
    	$("#ar_"+colposition+"_Patient_uid").val('');
	}
}