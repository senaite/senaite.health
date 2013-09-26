(function( $ ) {
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');

    isaraddview = (window.location.href.search('/ar_add') >= 0);
    comefrompatient = document.referrer.search('/patients/') >= 0;

    if (isaraddview && comefrompatient) {    	
        /* AR Add View. Automatically fill the Patient, and Client fields */
        pid = document.referrer.split("/patients/")[1].split("/")[0];
        $.ajax({
            url: window.portal_url + "/getpatientinfo",
            type: 'POST',
            data: {'_authenticator': $('input[name="_authenticator"]').val(),
                   'PatientID': pid,},
            dataType: "json",
            success: function(data, textStatus, $XHR){
                for (var col=0; col<parseInt($("#col_count").val()); col++) {
                    if (data['PatientUID']!='') {        	        	
                        $("#ar_"+col+"_Patient").val(data['PatientFullname']);
                        $("#ar_"+col+"_Patient").attr('uid', data['PatientUID']);
                        $("#ar_"+col+"_Patient_uid").val(data['PatientUID']);
                        $("#ar_"+col+"_ClientPatientID").val(data['ClientPatientID']);
                        $("#ar_"+col+"_ClientPatientID").attr('uid', data['PatientUID']);
                        $("#ar_"+col+"_ClientPatientID_uid").val(data['PatientUID']);
                        $("#ar_"+col+"_Patient").attr("readonly",true);
                        $("#ar_"+col+"_ClientPatientID").attr("readonly",true);
                    }
                }
            }
        });
    }

	// Mod the Age if DOB is selected
    if ($("#Age").length) {
		$("#Age").live('change', function(){
			if (parseInt($(this).val()) > 0) {
				var d = new Date();
				year = d.getFullYear() - $(this).val();
				var dob = year + "-01-01";
				$("#BirthDate").val(dob);
				calculateAge();
				$("#BirthDateEstimated").attr('checked', true);
			} else {
				$("#BirthDate".val(""));
				calculateAge();
			}
		});
    }

	// Mod the Age if DOB is selected
	$("#BirthDate").live('change', function(){
		calculateAge();
	});

	$("#CountryState.country").live('change', function(){
		$("#PhysicalAddress.country").val($(this).val());
		populate_state_select("PhysicalAddress")
	});
	$("#CountryState.state").live('change', function(){
		$("#PhysicalAddress.state").val($(this).val());
		populate_state_select("PhysicalAddress")
	});
	$("#PhysicalAddress.country").live('change', function(){
		$("#CountryState.country").val($(this).val());
		populate_district_select("CountryState")
	});
	$("#PhysicalAddress.state").live('change', function(){
		$("#CountryState.state").val($(this).val());
		populate_district_select("CountryState")
	});
	$("#patient-base-edit #Anonymous").live('change', function() {
		loadAnonymous();
	});
	$("#patient-base-edit #ClientPatientID").live('change', function() {
		if ($('#patient-base-edit #Anonymous').is(':checked')) {
			$("#patient-base-edit input[id='Surname']").val($("#patient-base-edit #ClientPatientID").val());
		}
	});

	function calculateAge() {
		var dob = new Date($("#BirthDate").val());
		var now = new Date();
		if (dob!= undefined && dob != null && now>=dob){
			var now = new Date();
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

		    if ($("#Age").length) { $("#Age").val(ageyear); }
			$("#AgeSplitted_year").val(ageyear);
			$("#AgeSplitted_month").val(agemonth);
			$("#AgeSplitted_day").val(ageday);

		} else {

		    if ($("#Age").length) { $("#Age").val(''); }
			$("#AgeSplitted_year").val('');
			$("#AgeSplitted_month").val('');
			$("#AgeSplitted_day").val('');
		}
		$("#BirthDateEstimated").attr('checked', false);
	}
	
	// These are not meant to show up in the main patient base_edit form.
	// they are flagged 'visible' though, so they do show up when requested.
	$('.template-base_edit #archetypes-fieldname-Allergies').hide();
	$('.template-base_edit #archetypes-fieldname-TreatmentHistory').hide();
	$('.template-base_edit #archetypes-fieldname-ImmunizationHistory').hide();
	$('.template-base_edit #archetypes-fieldname-TravelHistory').hide();
	$('.template-base_edit #archetypes-fieldname-ChronicConditions').hide();
	
	// Show menstrual status only if patient is female
	$('#archetypes-fieldname-Gender #Gender').live('change', function(){
		if ($('#archetypes-fieldname-MenstrualStatus').length){
			if (this.value=='female') {
				$('#archetypes-fieldname-MenstrualStatus').show();								
			} else {
				$("#MenstrualStatus-Hysterectomy-0").attr('checked', false);
				$("#MenstrualStatus-HysterectomyYear-0").val('');
				$("#MenstrualStatus-OvariesRemoved-0").attr('checked', false);
				$("#MenstrualStatus-OvariesRemovedNum-0:radio").attr('checked', false);
				$("#MenstrualStatus-OvariesRemovedYear-0").val('');
				$('#archetypes-fieldname-MenstrualStatus').hide();
			}
		}
	});
	if ($('#archetypes-fieldname-Gender #Gender').val()!='female') {
		$('#archetypes-fieldname-MenstrualStatus').hide();
	}
	
	if ($('#patient-base-edit')) {
		loadAnonymous();
	}

});
}(jQuery));

$.urlParam = function(name){
    var results = new RegExp('[\\?&amp;]' + name + '=([^&amp;#]*)').exec(window.location.href);
    return results != null ? results[1] : null;
}

function loadAnonymous() {
	tohide = ["#patient-base-edit #archetypes-fieldname-Salutation",
	          "#patient-base-edit #archetypes-fieldname-Middleinitial",
	          "#patient-base-edit #archetypes-fieldname-Middlename",
	          "#patient-base-edit #archetypes-fieldname-Firstname",
              "#patient-base-edit #archetypes-fieldname-Surname",
              "#patient-base-edit #archetypes-fieldname-AgeSplitted",
              "#patient-base-edit #archetypes-fieldname-BirthDateEstimated"];
	
	if ($('#patient-base-edit #Anonymous').is(':checked')) {		
		// Hide non desired input fields
		for (i=0;i<tohide.length;i++){
			$(tohide[i]).hide();
		}		
		// Set default values
		$("#patient-base-edit #ClientPatientID").attr("required", true);
		$("#patient-base-edit #ClientPatientID_help").before('<span class="required" title="Required">&nbsp;</span>');
		$("#patient-base-edit input[id='Firstname']").val(_("AP"));
		cpid = $("#patient-base-edit #ClientPatientID").val();
		if (cpid && cpid.length > 0) {
			$("#patient-base-edit input[id='Surname']").val(cpid);
		} else {
			$("#patient-base-edit input[id='Surname']").val("-");
		}
		$("#patient-base-edit #archetypes-fieldname-BirthDate").find('span[class="required"]').remove();
		$("#patient-base-edit input[id='BirthDate']").attr("required", false);
		$("#patient-base-edit input[id='BirthDate']").val("");		
		
	} else {
		// Show desired input fields
		for (i=0;i<tohide.length;i++){
			$(tohide[i]+":hidden").show();
		}
		$("#patient-base-edit #archetypes-fieldname-ClientPatientID").find('span[class="required"]').remove();
		$("#patient-base-edit input[id='ClientPatientID']").attr("required", false);
		$("#patient-base-edit input[id='BirthDate']").attr("required", true);
		$("#patient-base-edit #BirthDate_help").before('<span class="required" title="Required">&nbsp;</span>');		
	}
}
