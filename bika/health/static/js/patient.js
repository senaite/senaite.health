(function( $ ) {
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');

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
							dateFormat: dateFormat,
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
								$(".jsPatientTitle").remove();
								$("#archetypes-fieldname-PatientID").append("<span class='jsPatientTitle'><a class='edit_patient' href='"+window.portal_url+"/patients/"+data['PatientID']+"/edit'>"+Fullname+"</a></span>");
								$('a.edit_patient').prepOverlay(editpatient_overlay);
								$("#Client").val(data['ClientID']);
								$(".jsClientTitle").remove();
								$("#archetypes-fieldname-ClientID").append("<span class='jsClientTitle'><a href='"+window.portal_url+"/clients/"+data['ClientSysID']+"/base_edit'>"+data['ClientTitle']+"</a></span>");
								$('input[name="PatientBirthDate"]').val(data['PatientBirthDate']);
								if ($('input[name="PatientGender"]').length == 0){
									$("body").append('<input type="hidden" name="PatientGender"/>');
									
									$('input[name="PatientGender"]').change(function(){
										gender = $('input[name="PatientGender"]').val();
										if ($("#Symptoms_table").length) {
											// Show/Hide the symptoms according to Patient's gender
											// Hide/shows symptoms items according to selected gender
											$("#Symptoms_table tr.symptom-item").find('td').hide();
											$("#Symptoms_table tr.symptom-item.gender-"+gender).find('td').show();
											$("#Symptoms_table tr.symptom-item.gender-dk").find('td').show();		
										}
										if ($('#archetypes-fieldname-MenstrualStatus').length){
											// Show/Hide MenstrualStatus widget depending on patient's gender
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
									});						
								}
								$('input[name="PatientGender"]').val(data['PatientGender']);
								$('input[name="PatientGender"]').change();
							}
						});
					}
				}
			}
		}

	// Add Patient popup
	if($(".portaltype-patient").length == 0 &&
	   window.location.href.search('portal_factory/Patient') == -1){
			$("input[id=PatientID]").after('<a style="border-bottom:none !important;margin-left:.5;"' +
						' class="add_patient"' +
						' href="'+window.portal_url+'/patients/portal_factory/Patient/new/edit"' +
						' rel="#overlay">' +
						' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
					' </a>');
		$("input[id=PatientID]").combogrid({
			colModel: [{'columnName':'PatientUID','hidden':true},
					   {'columnName':'PatientID','width':'20','label':_('Patient ID')},
					   {'columnName':'Title','width':'40','label':_('Full name')},
					   {'columnName':'AdditionalIdentifiers', 'width':'40','label':_('Additional Identifiers')},
					   {'columnName':'PatientBirthDate','hidden':true},
					   {'columnName':'PatientGender', 'hidden':true},
					   {'columnName':'MenstrualStatus', 'hidden':true}],
			url: window.portal_url + "/getpatients?_authenticator=" + $('input[name="_authenticator"]').val(),
            width: "650px",
			rows:5,
			showOn: true,
			select: function( event, ui ) {
				$(this).val(ui.item.PatientID);
				$(this).parents('tr').find('input[id=AdditionalIdentifiers]').val(ui.item.AdditionalIdentifiers);
				$(this).change();
				if($(".portaltype-batch").length > 0 && $(".template-base_edit").length > 0) {
					$(".jsPatientTitle").remove();
					$("#archetypes-fieldname-PatientID").append("<span class='jsPatientTitle'><a class='edit_patient' href='"+window.portal_url+"/patients/"+ui.item.PatientID+"/edit'>"+ui.item.Title+"</a></span>");
					$('a.edit_patient').prepOverlay(editpatient_overlay);
					$("#ClientID").val(ui.item.ClientID);
					$(".jsClientTitle").remove();
					$("#archetypes-fieldname-ClientID").append("<span class='jsClientTitle'><a href='"+window.portal_url+"/clients/"+ui.item.ClientSysID+"/base_edit'>"+ui.item.ClientTitle+"</a></span>");
					if($('input[name="PatientBirthDate"]').length == 0){
						$("body").append('<input type="hidden" name="PatientBirthDate"/>');
					}
					$('input[name="PatientBirthDate"]').val(ui.item.PatientBirthDate);
					if ($('input[name="PatientGender"]').length == 0){
						$("body").append('<input type="hidden" name="PatientGender"/>');
						
						$('input[name="PatientGender"]').change(function(){
							gender = $('input[name="PatientGender"]').val();
							if ($("#Symptoms_table").length) {
								// Show/Hide the symptoms according to Patient's gender
								// Hide/shows symptoms items according to selected gender
								$("#Symptoms_table tr.symptom-item").find('td').hide();
								$("#Symptoms_table tr.symptom-item.gender-"+gender).find('td').show();
								$("#Symptoms_table tr.symptom-item.gender-dk").find('td').show();		
							}
							if ($('#archetypes-fieldname-MenstrualStatus').length){
								// Show/Hide MenstrualStatus widget depending on patient's gender
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
						});						
					}
					$('input[name="PatientGender"]').val(ui.item.PatientGender);
					$('input[name="PatientGender"]').change();
					
					// Set patient's menstrual status
					if ($('#archetypes-fieldname-MenstrualStatus').length){
						ms = ui.item.MenstrualStatus;
						if (ms!=null && ms.length > 0) {
							ms = ms[0];
							
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
					}
					
				}
				return false;
			}
		});
	}

	$('a.add_patient').prepOverlay(editpatient_overlay);
	$('a.edit_patient').prepOverlay(editpatient_overlay);

	// Mod the Age if DOB is selected
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

			$("#Age").val(ageyear);
			$("#AgeSplitted_year").val(ageyear);
			$("#AgeSplitted_month").val(agemonth);
			$("#AgeSplitted_day").val(ageday);

		} else {

			$("#Age").val('');
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

});
}(jQuery));
