// JS for <batch_id>/base_edit form

function init() {
    if (!$('input[name="PatientBirthDate"]').length) {
        $("body").append('<input type="hidden" name="PatientBirthDate"/>');
    }
    if (!$('input[name="PatientGender"]').length){
        $("body").append('<input type="hidden" name="PatientGender"/>');
    }
}

function loadEventHandlers() {
    $("#Patient").bind("selected paste blur", function(){
    	loadPatientData();
    	filterByClientIfNeeded();
    });
    $("#Doctor").bind("selected paste blur", function(){
    	loadDoctorOverlay(null);
    });
    $("#OnsetDate").live('change', function() {
        setPatientAgeAtCaseOnsetDate();
    });
    $("#ClientPatientID").bind("selected paste blur", function() {
		id = $(this).val()
    	loadAnonymousPatient(id);
		filterByClientIfNeeded();
    });
}

function loadAnonymousPatient(id) {
	if (id!='') {
		$.ajax({
			url: window.portal_url + "/getpatientinfo",
			type: 'POST',
			data: {'_authenticator': $('input[name="_authenticator"]').val(),
                   'ClientPatientID': id},
        dataType: "json",
        success: function(data, textStatus, $XHR){
        	if (data['PatientUID']!='') {
	        	$("#Patient").val(data['PatientFullname']);
	        	$("#Patient").attr('uid', data['PatientUID']);
	        	$("#Patient_uid").val(data['PatientUID']);
        	} else {
        		// No patient found. Set empty patient
        		$("#Patient").val('');
	        	$("#Patient").attr('uid', '');
	        	$("#Patient_uid").val('');
        	}
        }
		});
	}
	loadPatientData();
}


function loadPatientData() {
    $('input[name="PatientBirthDate"]').val('');
    $('input[name="PatientGender"]').val('');
    $('a.edit_patient').remove();
    patientuid = $("#Patient").attr('uid');
    if (patientuid) {
        $.ajax({
            url: window.portal_url + "/getpatientinfo",
            type: 'POST',
            data: {'_authenticator': $('input[name="_authenticator"]').val(),
                    'PatientUID': patientuid},
            dataType: "json",
            success: function(data, textStatus, $XHR){
                // Override client values only if client hasn't been selected
	            if ($('input[name="Client_uid"]').val().length == 0) {
	                $('input[name="Client"]').val(data['ClientTitle']);
	                $('input[name="Client"]').attr('uid', data['ClientUID']);
	                $('input[name="Client_uid"]').val(data['ClientUID']);
        		}
                $('input[name="PatientBirthDate"]').val(data['PatientBirthDate']);
                $('input[name="PatientGender"]').val(data['PatientGender']);
                $('input[name="ClientPatientID"]').val(data['ClientPatientID']);
                
                // Set patient's menstrual status
                if (data['PatientGender'] == 'female'
                    && data['PatientMenstrualStatus'] != null
                    && data['PatientMenstrualStatus'].length > 0) {
                    ms = data['PatientMenstrualStatus'][0];
                    // Set hysterectomy fields
                    $("#MenstrualStatus-Hysterectomy-0").attr('checked', ms['Hysterectomy']);
                    $("#MenstrualStatus-HysterectomyYear-0").val(ms['HysterectomyYear']);
                    if (!ms['Hysterectomy']) {
                        $("#MenstrualStatus-HysterectomyYear-0").val('');
                        $("#MenstrualStatus-HysterectomyYear-0").parent().hide();
                    } else {
                        $("#MenstrualStatus-HysterectomyYear-0").parent().show();
                        $("#MenstrualStatus-HysterectomyYear-0").focus()
                    }

                    // Set ovaries removed fields
                    $("#MenstrualStatus-OvariesRemoved-0").attr('checked', ms['OvariesRemoved']);
                    $("#MenstrualStatus-OvariesRemovedNum-0[value=1]").attr('checked',ms['OvariesRemovedNum']==1);
                    $("#MenstrualStatus-OvariesRemovedNum-0[value=2]").attr('checked',ms['OvariesRemovedNum']==2);
                    $("#MenstrualStatus-OvariesRemovedYear-0").val(ms['OvariesRemovedYear']);
                    if (!ms['OvariesRemoved']) {
                        $("#MenstrualStatus-OvariesRemovedNum-0:radio").attr('checked', false);
                        $("#MenstrualStatus-OvariesRemovedYear-0").val('');
                        $("#MenstrualStatus-OvariesRemovedYear-0").parent().hide();
                    } else {
                        $("#MenstrualStatus-OvariesRemovedYear-0").parent().show();
                    }
                }
                loadPatientOverlay(data['PatientID']);
                setPatientAgeAtCaseOnsetDate();
                loadMenstrualStatus();
                loadSymptoms();
            }
        });
    }
}

function loadSymptoms() {
    if ($("#Symptoms_table").length) {
        // Show/Hide the symptoms according to Patient's gender
        gender = $('input[name="PatientGender"]').val();
        $("#Symptoms_table tr.symptom-item").find('td').hide();
        $("#Symptoms_table tr.symptom-item.gender-"+gender).find('td').show();
        $("#Symptoms_table tr.symptom-item.gender-dk").find('td').show();
    }
}

function loadMenstrualStatus() {
    if ($('#archetypes-fieldname-MenstrualStatus').length){
        // Show/Hide MenstrualStatus widget depending on patient's gender
        gender = $('input[name="PatientGender"]').val();
        if (gender=='female') {
            $('#archetypes-fieldname-MenstrualStatus').show();
        } else {
            $("#MenstrualStatus-FirstDayOfLastMenses-0").val('');
            $("#MenstrualCycleType-0").val('');
            $("#MenstrualStatus-Pregnant-0").attr('checked', false);
            $("#MenstrualStatus-MonthOfPregnancy-0").val('');
            $("#MenstrualStatus-Hysterectomy-0").attr('checked', false);
            $("#MenstrualStatus-HysterectomyYear-0").val('');
            $("#MenstrualStatus-OvariesRemoved-0").attr('checked', false);
            $("#MenstrualStatus-OvariesRemovedNum-0:radio").attr('checked', false);
            $("#MenstrualStatus-OvariesRemovedYear-0").val('');
            $('#archetypes-fieldname-MenstrualStatus').hide();
        }
    }
}

function setPatientAgeAtCaseOnsetDate() {
    var now = new Date($("#OnsetDate").val());
    var dob = new Date($('input[name="PatientBirthDate"]').val());
    if (now!= undefined && now != null && dob!=undefined && dob != null && now >= dob){
        var currentday=now.getDate();
        var currentmonth=now.getMonth()+1;
        var currentyear=now.getFullYear();
        var birthday=dob.getDate();
        var birthmonth=dob.getMonth()+1;
        var birthyear=dob.getFullYear();
        var ageday = currentday-birthday;
        var agemonth=0;
        var ageyear=0;

        if (ageday < 0) {
            currentmonth--;
            if (currentmonth < 1) {
                currentyear--;
                currentmonth = currentmonth + 12;
            }
            dayspermonth = 30;
            if (currentmonth==1 || currentmonth==3 ||
                currentmonth==5 || currentmonth==7 ||
                currentmonth==8 || currentmonth==10||
                currentmonth==12) {
                dayspermonth = 31;
            } else if (currentmonth == 2) {
                dayspermonth = 28;
                if(!(currentyear%4) && (currentyear%100 || !(currentyear%400))) {
                    dayspermonth++;
                }
            }
            ageday = ageday + dayspermonth;
        }

        agemonth = currentmonth - birthmonth;
        if (agemonth < 0) {
            currentyear--;
            agemonth = agemonth + 12;
        }
        ageyear = currentyear - birthyear;

        $("#PatientAgeAtCaseOnsetDate_year").val(ageyear);
        $("#PatientAgeAtCaseOnsetDate_month").val(agemonth);
        $("#PatientAgeAtCaseOnsetDate_day").val(ageday);

    } else {
        $("#PatientAgeAtCaseOnsetDate_year").val('');
        $("#PatientAgeAtCaseOnsetDate_month").val('');
        $("#PatientAgeAtCaseOnsetDate_day").val('');
    }
}

function loadPatientOverlay(patientId) {
    if (!$('a.add_patient').length) {
        $("input[id=Patient]").after('<a style="border-bottom:none !important;margin-left:.5;"' +
                ' class="add_patient"' +
                ' href="'+window.portal_url+'/patients/portal_factory/Patient/new/edit"' +
                ' rel="#overlay">' +
                ' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
            ' </a>');
    }
    $('a.add_patient').prepOverlay(getPatientOverlay());
    
    $('a.edit_patient').remove();
	if (patientId == null && $('input[name="Patient_uid"]').val().length > 0) {
		$.ajax({
            url: window.portal_url + "/getpatientinfo",
            type: 'POST',
            data: {'_authenticator': $('input[name="_authenticator"]').val(),
                    'PatientUID': $('input[name="Patient_uid"]').val()},
            dataType: "json",
            success: function(data, textStatus, $XHR){
            	loadPatientOverlay(data['PatientID']);
            }
        });
	} else if (patientId != null) {
		$("a.add_patient").after('<a style="border-bottom:none !important;margin-left:.5;"' +
	            ' class="edit_patient"' +
	            ' href="'+window.portal_url+'/patients/portal_factory/Patient/'+patientId+'/edit"' +
	            ' rel="#overlay">Edit' +
        ' </a>');
	    $('a.edit_patient').prepOverlay(getPatientOverlay());
	}
}

function loadDoctorOverlay(doctorId) {
	if (!$('a.add_doctor').length) {
        $("input[id=Doctor]").after('<a style="border-bottom:none !important;margin-left:.5;"' +
                ' class="add_doctor"' +
                ' href="'+window.portal_url+'/doctors/portal_factory/Doctor/new/edit"' +
                ' rel="#overlay">' +
                ' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
            ' </a>');
    }
	$('a.add_doctor').prepOverlay(getDoctorOverlay());

	$('a.edit_doctor').remove();
	if (doctorId == null && $('input[name="Doctor_uid"]').val().length > 0) {
		$.ajax({
            url: window.portal_url + "/getdoctorinfo",
            type: 'POST',
            data: {'_authenticator': $('input[name="_authenticator"]').val(),
                    'UID': $('input[name="Doctor_uid"]').val()},
            dataType: "json",
            success: function(data, textStatus, $XHR){
            	loadDoctorOverlay(data['id']);            	
            }
        });
	} else if (doctorId != null){
		$("a.add_doctor").after('<a style="border-bottom:none !important;margin-left:.5;"' +
	            ' class="edit_doctor"' +
	            ' href="'+window.portal_url+'/doctors/portal_factory/Doctor/'+doctorId+'/edit"' +
	            ' rel="#overlay">Edit' +
        ' </a>');
	    $('a.edit_doctor').prepOverlay(getDoctorOverlay());
	}
}

function getDoctorOverlay() {
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
                if (Fullname.length > 1) {
                    $.ajax({
                        url: window.portal_url + "/getdoctorinfo",
                        type: 'POST',
                        data: {'_authenticator': $('input[name="_authenticator"]').val(),
                                'Fullname': Fullname},
                        dataType: "json",
                        success: function(data, textStatus, $XHR){
                            $("#Doctor").val(data['Fullname']);
                            $("#Doctor").attr('uid', data['UID']);
                            $("#Doctor_uid").val(data['UID']);
                            loadDoctorOverlay(data['id']);
                        }
                    });
                }
            }
        }
    }
    return editdoctor_overlay;
}

function getPatientOverlay() {
    dateFormat = _b("date_format_short_datepicker");
    editpatient_overlay = {
        subtype: 'ajax',
        filter: 'head>*,#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
        formselector: '#patient-base-edit',
        closeselector: '[name="form.button.cancel"]',
        width:'70%',
        noform:'close',
        config: {
            onLoad: function() {
                // manually remove remarks
                this.getOverlay().find("#archetypes-fieldname-Remarks").remove();
                // remove menstrual status widget (accesible from case)
                this.getOverlay().find("#archetypes-fieldname-MenstrualStatus").remove();
                // reapply datepicker widget
                this.getOverlay().find("#BirthDate").live('click', function() {
                    $(this).datepicker({
                        showOn:'focus',
                        showAnim:'',
                        changeMonth:true,
                        changeYear:true,
                        maxDate: '+0d',
                        dateFormat: _b("date_format_short_datepicker"),
                        yearRange: "-100:+0"
                    })
                    .click(function(){$(this).attr('value', '');})
                    .focus();
                });

                // Address widget
                $.ajax({
                    url: 'bika_widgets/addresswidget.js',
                    dataType: 'script',
                    async: false
                });

            },
            onClose: function() {
                var Fullname = $("#Firstname").val() + " " + $("#Surname").val();
                if (Fullname.length > 1) {
                    $.ajax({
                        url: window.portal_url + "/getpatientinfo",
                        type: 'POST',
                        data: {'_authenticator': $('input[name="_authenticator"]').val(),
                                'Fullname': Fullname},
                        dataType: "json",
                        success: function(data, textStatus, $XHR){
                            $("#Patient").val(data['PatientFullname']);
                            $("#Patient").attr('uid', data['PatientUID']);
                            $("#Patient_uid").val(data['PatientUID']);
                            loadPatientData();
                            //$("#Client").val(data['ClientTitle']);
                            //$("#Client_uid").val(data['ClientUID']);
                        }
                    });
                }
            }
        }
    }
    return editpatient_overlay;
}

/**
 * Restricts the search results of Patient's reference widgets (Patient and
 * ClientPatientID) to current client if the current page comes from a Client's
 * batch view. If no current client found, does nothing.
 */
function filterByClientIfNeeded() {
	clientuid = getReferrerClientUID();
	if (clientuid != null) {
		base_query=$.parseJSON($("#Patient").attr("base_query"));
		base_query['getPrimaryReferrerUID'] = clientuid;
		options = $.parseJSON($("#Patient").attr("combogrid_options"));
		options['force_all']='false';
		$("#Patient").attr("base_query", $.toJSON(base_query));
		$("#Patient").attr("combogrid_options", $.toJSON(options));		
		referencewidget_lookups($("#Patient"));
		
		base_query=$.parseJSON($("#ClientPatientID").attr("base_query"));
		base_query['getPrimaryReferrerUID'] = clientuid;
		options = $.parseJSON($("#ClientPatientID").attr("combogrid_options"));
		options['force_all']='false';
		$("#ClientPatientID").attr("base_query", $.toJSON(base_query));
		$("#ClientPatientID").attr("combogrid_options", $.toJSON(options));
		referencewidget_lookups($("#ClientPatientID"));
	}
}

default_client_uid = null;
/**
 * Returns the current client UID if the current page referral is a Client's
 * batch view. If no current client found, returns null
 * @returns the current Client UID or null
 */
function getReferrerClientUID() {	
	if (default_client_uid == null) {
		clientid = null;
		if (document.referrer.search('/clients/') >= 0) {    	
	    	clientid = document.referrer.split("clients")[1].split("/")[1];
		}
		if (clientid != null) {
			$.ajax({
				url: window.portal_url + "/clients/" + clientid + "/getClientInfo",
				type: 'POST',
				data: {'_authenticator': $('input[name="_authenticator"]').val()},
	        dataType: "json",
	        success: function(data, textStatus, $XHR){
	        	if (data['ClientUID'] != '') {
	        		default_client_uid = data['ClientUID'];
	        	}
	        }
			});
		}
	}
	return default_client_uid;
} 

(function( $ ) {
$(document).ready(function(){

	_p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _  = jarn.i18n.MessageFactory('bika.health');

    // These look silly in the edit screen under "Additional Notes"
    $("#archetypes-fieldname-Remarks").remove();
    
	// Check for missing hidden data
	init();
	
    // Restrict results to current client if needed
	filterByClientIfNeeded();

	// Load events
	loadEventHandlers();

	// Load additional Patient data, like birth date, age, etc.
	// If a client has already been selected, it doesn't get overrided
	loadPatientData();

	// Load patient add/edit overlay	
	loadPatientOverlay(null);
	
	// Load doctor add/edit overlay
	loadDoctorOverlay(null);	

});
}(jQuery));
