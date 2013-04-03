// JS for <batch_id>/base_edit form
(function( $ ) {
$(document).ready(function(){
	
	_p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _  = jarn.i18n.MessageFactory('bika.health');
    
	// Check for missing hidden data
	init()

	// Load events
	loadEventHandlers();	

	// Load patient selector popup
	loadPatientCombogrid();
	
	// Load additional Patient data, like birth date, age, etc.
	loadPatientData();
	
	// Load patient add/edit overlay
	loadPatientOverlay();
	
	if ($("input[id=PatientID]").val().length == 0) {
		$("input[id=PatientID]").focus();
	}
	
	
	function init() {
		if (!$('input[name="PatientBirthDate"]').length) {
			$("body").append('<input type="hidden" name="PatientBirthDate"/>');
		}		
		if (!$('input[name="PatientGender"]').length){
			$("body").append('<input type="hidden" name="PatientGender"/>');
		}
	}
	
	function loadEventHandlers() {
		$("#PatientID").live('change', function() {
			loadPatientData();			
		});	
		$("#OnsetDate").live('change', function() {
			setPatientAgeAtCaseOnsetDate();
		});
		$("#PatientID").live('focus', function() {
			$("#PatientID").val('');
		});
		$("#DoctorID").live('focus', function() {
			$("#DoctorID").val('');
		});
	}

	function loadPatientCombogrid() {

    	urlpatients = window.portal_url + "/getpatients?_authenticator=" + $('input[name="_authenticator"]').val();
		if (document.referrer.search('/clients/') >= 0) {
			/* Set automatically the client to the batch and only show
			 * the patients for that client in patients combogrid */
	    	clientid = document.referrer.split("clients")[1].split("/")[1];
	    	urlpatients += "&clientid="+clientid;
	    	$.ajax({
	    		url: window.portal_url+"/clients/"+clientid+"/getClientInfo",
	    		type: 'POST',
	    		data: {'_authenticator': $('input[name="_authenticator"]').val()},
	            dataType: "json",
	            success: function(data, textStatus, $XHR){            	
	            	$("#ClientID").val(data['ClientID']);
	            	$("#ClientID").attr('readonly', true);
					$(".jsClientTitle").remove();
					$("#archetypes-fieldname-ClientID").append("<span class='jsClientTitle'><a class='anchor_client' href='"+window.portal_url+"/clients/"+data['ClientSysID']+"/base_edit'>"+data['ClientTitle']+"</a></span>");
	            }
	    	});
		}
		$("input[id=PatientID]").combogrid({
			colModel: [{'columnName':'PatientUID','hidden':true},
					   {'columnName':'PatientID','width':'20','label':_('Patient ID')},
					   {'columnName':'Title','width':'40','label':_('Full name')},
					   {'columnName':'AdditionalIdentifiers', 'width':'40','label':_('Additional Identifiers')}],
			url: urlpatients,
		    width: "650px",
			rows:5,
			showOn: true,
			select: function( event, ui ) {
				$(this).val(ui.item.PatientID);
				$(this).parents('tr').find('input[id=AdditionalIdentifiers]').val(ui.item.AdditionalIdentifiers);
				$(this).change();
				return false;
			}
		});
	}
	
	function loadPatientData() {
		$(".jsClientTitle").remove();	
		$(".jsPatientTitle").remove();
		$('input[name="ClientID"]').val('');
		$('input[name="PatientBirthDate"]').val('');
		$('input[name="PatientGender"]').val('');
		patientid = $("#PatientID").val();
		if (patientid.length > 0) {
			$.ajax({
				url: window.portal_url + "/getpatientinfo",
				type: 'POST',
				data: {'_authenticator': $('input[name="_authenticator"]').val(),
						'PatientID': patientid},
				dataType: "json",
				success: function(data, textStatus, $XHR){
					$('input[name="ClientID"]').val(data['ClientID']);
					$('input[name="PatientBirthDate"]').val(data['PatientBirthDate']);
					$('input[name="PatientGender"]').val(data['PatientGender']);
					$("#archetypes-fieldname-ClientID").append("<span class='jsClientTitle'><a href='"+window.portal_url+"/clients/"+data['ClientSysID']+"/base_edit'>"+data['ClientTitle']+"</a></span>");
	                $("#archetypes-fieldname-PatientID").append("<span class='jsPatientTitle'><a class='edit_patient' href='"+window.portal_url+"/patients/"+data['PatientID']+"/edit'>"+data['PatientFullname']+"</a></span>");
					$('a.edit_patient').prepOverlay(getPatientOverlay());
										
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
					setPatientAgeAtCaseOnsetDate();
					loadMenstrualStatus();
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
		
	function loadPatientOverlay() {
		if (!$('a.add_patient').length) {
			$("input[id=PatientID]").after('<a style="border-bottom:none !important;margin-left:.5;"' +
					' class="add_patient"' +
					' href="'+window.portal_url+'/patients/portal_factory/Patient/new/edit"' +
					' rel="#overlay">' +
					' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
				' </a>');
		}
		$('a.add_patient').prepOverlay(getPatientOverlay());		
		$('a.edit_patient').prepOverlay(getPatientOverlay());
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
								$("#PatientID").val(data['PatientID']);
								$("#PatientID").change();
							}
						});
					}
				}
			}
		}
		return editpatient_overlay;
	}
	
});
}(jQuery));



