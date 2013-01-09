(function( $ ) {
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');

	dateFormat = _b("date_format_short_datepicker");

	// Add Patient popup
	if($(".portaltype-patient").length == 0 &&
	   window.location.href.search('portal_factory/Patient') == -1){
			$("input[id=Patient]").after('<a style="border-bottom:none !important;margin-left:.5;"' +
						' class="add_patient"' +
						' href="'+window.portal_url+'/patients/portal_factory/Patient/new/edit"' +
						' rel="#overlay">' +
						' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
					' </a>');
		$("input[id=Patient]").combogrid({
			colModel: [{'columnName':'PatientUID','hidden':true},
					   {'columnName':'PatientID','width':'20','label':_('Patient ID')},
					   {'columnName':'Title','width':'40','label':_('Full name')},
					   {'columnName':'AdditionalIdentifiers', 'width':'40','label':_('Additional Identifiers')},
					   {'columnName':'PatientBirthDate','hidden':true}],
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
					$("#archetypes-fieldname-Patient").append("<span class='jsPatientTitle'>"+ui.item.Title+"</span>");
					$("#Client").val(ui.item.ClientID);
					$(".jsClientTitle").remove();
					$("#archetypes-fieldname-Client").append("<span class='jsClientTitle'>"+ui.item.ClientTitle+"</span>");
					if($('input[name="PatientBirthDate"]').length == 0){
						$("body").append('<input type="hidden" name="PatientBirthDate"/>');
					}
					$('input[name="PatientBirthDate"]').val(ui.item.PatientBirthDate);
				}
				return false;
			}
		});
	}

	$('a.add_patient').prepOverlay(
		{
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

					// These are not meant to show up in the main patient base_edit form.
					// they are flagged 'visible' though, so they do show up when requested.
					$('.template-base_edit #archetypes-fieldname-Allergies').hide();
					$('.template-base_edit #archetypes-fieldname-TreatmentHistory').hide();
					$('.template-base_edit #archetypes-fieldname-ImmunizationHistory').hide();
					$('.template-base_edit #archetypes-fieldname-TravelHistory').hide();
					$('.template-base_edit #archetypes-fieldname-ChronicConditions').hide();

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
								$("#Patient").val(data['PatientID']);
								$(".jsPatientTitle").remove();
								$("#archetypes-fieldname-Patient").append("<span class='jsPatientTitle'>"+Fullname+"</span>");
								$("#Client").val(data['ClientID']);
								$(".jsClientTitle").remove();
								$("#archetypes-fieldname-Client").append("<span class='jsClientTitle'>"+data['ClientTitle']+"</span>");
								$('input[name="PatientBirthDate"]').val(data['PatientBirthDate']);
							}
						});
					}
				}
			}
		}
	);

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

});
}(jQuery));
