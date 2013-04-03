(function( $ ) {
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');

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
