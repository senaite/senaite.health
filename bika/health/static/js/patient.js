(function( $ ) {
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');

	dateFormat = _b("date_format_short_datepicker");

	// Add Patient popup
	if($(".portaltype-patient").length == 0 &&
	   window.location.href.search('portal_factory/Patient') == -1){
			$("input[id=PatientID]").after('<a style="border-bottom:none !important;margin-left:.5;"' +
						' class="add_patient"' +
						' href="'+window.portal_url+'/patients/portal_factory/Patient/new/edit"' +
						' rel="#overlay">' +
						' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
					' </a>');
		$("input[id*=PatientID]").combogrid({
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
					$("#archetypes-fieldname-PatientID").append("<span class='jsPatientTitle'>"+ui.item.Title+"</span>");
					$("#ClientID").val(ui.item.ClientID);
					$(".jsClientTitle").remove();
					$("#archetypes-fieldname-Client").append("<span class='jsClientTitle'>"+ui.item.ClientTitle+"</span>");
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

				},
				onClose: function() {
					var Fullname = $("#Firstname").val() + " " + $("#Surname").val();
					if (Fullname.length > 1) {
						$.ajax({
							url: window.portal_url + "/getPatientInfo",
							type: 'POST',
							data: {'_authenticator': $('input[name="_authenticator"]').val(),
									'Fullname': Fullname},
							dataType: "json",
							success: function(data, textStatus, $XHR){
								$("#PatientID").val(data['PatientID']);
								$(".jsPatientTitle").remove();
								$("#archetypes-fieldname-PatientID").append("<span class='jsPatientTitle'>"+Fullname+"</span>");
								$("#ClientID").val(data['ClientID']);
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

	$(".template-treatmenthistory .add_row").click(function(event){
		event.preventDefault();
		D = $("#Drug").val();
		S = $("#Start").val();
		E = $("#End").val();
		if (D == '') {
			return false;
		}
		if (Date.parse(E) < Date.parse(S)) {
			alert(_('End date must be after start date'))
			return false;
		}
		$("#Start").attr('class', 'datepicker_nofuture');
		$("#End").attr('class', 'datepicker');

		newrow = $("tr#new").clone();
		$("tr#new").removeAttr('id');
		$("#Drug").parent().append("<span>"+D+"</span>");
		$("#Drug").parent().append("<input type='hidden' name='Drug:list' value='"+D+"'/>");
		$("#Drug").remove();
		$("#Start").parent().append("<span>"+S+"</span>");
		$("#Start").parent().append("<input type='hidden' name='Start:list' value='"+S+"'/>");
		$("#Start").remove();
		$("#End").parent().append("<span>"+E+"</span>");
		$("#End").parent().append("<input type='hidden' name='End:list' value='"+E+"'/>");
		$("#End").remove();
		for(i=0; i<$(newrow).children().length; i++){
			td = $(newrow).children()[i];
			input = $(td).children()[0];
			$(input).val('');
		}
		$(newrow).appendTo($(".bika-listing-table"));
		lookups();
		return false;
	})

	$(".template-allergies .add_row").click(function(event){
		event.preventDefault();
		P = $("#DrugProhibition").val();
		D = $("#Drug").val();
		if (D == '' || P == '') {
			return false;
		}
		newrow = $("tr#new").clone();
		$("tr#new").removeAttr('id');
		$("#DrugProhibition").parent().append("<span>"+P+"</span>");
		$("#DrugProhibition").parent().append("<input type='hidden' name='DrugProhibition:list' value='"+P+"'/>");
		$("#DrugProhibition").remove();
		$("#Drug").parent().append("<span>"+D+"</span>");
		$("#Drug").parent().append("<input type='hidden' name='Drug:list' value='"+D+"'/>");
		$("#Drug").remove();
		for(i=0; i<$(newrow).children().length; i++){
			td = $(newrow).children()[i];
			input = $(td).children()[0];
			$(input).val('');
		}
		$(newrow).appendTo($(".bika-listing-table"));
		lookups();
		return false;
	})

	$(".template-immunizationhistory .add_row").click(function(event){
		event.preventDefault();
		I = $("#Immunization").val();
		V = $("#VaccinationCenter").val();
		D = $("#Date").val();
		if (I == ''){
			alert(_('Immunization field cannot be empty'));
			return false;
		}
		$("#Date").attr('class', 'datepicker_nofuture');

		newrow = $("tr#new").clone();
		$("tr#new").removeAttr('id');
		$("#Immunization").parent().append("<span>"+I+"</span>");
		$("#Immunization").parent().append("<input type='hidden' name='Immunization:list' value='"+I+"'/>");
		$("#Immunization").remove();
		$("#VaccinationCenter").parent().append("<span>"+V+"</span>");
		$("#VaccinationCenter").parent().append("<input type='hidden' name='VaccinationCenter:list' value='"+V+"'/>");
		$("#VaccinationCenter").remove();
		$("#Date").parent().append("<span>"+D+"</span>");
		$("#Date").parent().append("<input type='hidden' name='Date:list' value='"+D+"'/>");
		$("#Date").remove();
		for(i=0; i<$(newrow).children().length; i++){
			td = $(newrow).children()[i];
			input = $(td).children()[0];
			$(input).val('');
		}
		$(newrow).appendTo($(".bika-listing-table"));
		lookups();
		return false;
	})

	$(".template-chronicconditions .add_row").click(function(event){
		event.preventDefault();
		C = $("#Code").val();
		T = $("#Title").val();
		D = $("#Description").val();
		O = $("#Onset").val();
		E = $("#End").val();
		R = $("#Remarks").val();
		if (T == ''){
			return false;
		}
		$("#Onset").attr('class', 'datepicker_nofuture');
		$("#End").attr('class', 'datepicker');

		newrow = $("tr#new").clone();
		$("tr#new").removeAttr('id');
		$("#Code").parent().append("<span>"+C+"</span>");
		$("#Code").parent().append("<input type='hidden' name='Code:list' value='"+C+"'/>");
		$("#Code").remove();
		$("#Title").parent().append("<span>"+T+"</span>");
		$("#Title").parent().append("<input type='hidden' name='Title:list' value='"+T+"'/>");
		$("#Title").remove();
		$("#Description").parent().append("<span>"+D+"</span>");
		$("#Description").parent().append("<input type='hidden' name='Description:list' value='"+D+"'/>");
		$("#Description").remove();
		$("#Onset").parent().append("<span>"+O+"</span>");
		$("#Onset").parent().append("<input type='hidden' name='Onset:list' value='"+O+"'/>");
		$("#Onset").remove();
		$("#End").parent().append("<span>"+E+"</span>");
		$("#End").parent().append("<input type='hidden' name='End:list' value='"+E+"'/>");
		$("#End").remove();
		for(i=0; i<$(newrow).children().length; i++){
			td = $(newrow).children()[i];
			input = $(td).children()[0];
			$(input).val('');
		}
		$(newrow).appendTo($(".bika-listing-table"));
		lookups();
		return false;
	})

	$(".template-travelhistory .add_row").click(function(event){
		event.preventDefault();
		S = $("#TripStartDate").val();
		E = $("#TripEndDate").val();
		T = $("#Country").val();
		L = $("#Location").val();
		if (S == '') {
			alert(_('Trip start date not defined'))
			return false;
		}
		if (E != '') {
			if (Date.parse(E) < Date.parse(S)) {
				alert(_('End date must be after start date'))
				return false;
			}
		 }
		if (T == ''){
			alert(_('Country not defined'))
			return false;
		}

		$("#TripStartDate").attr('class', 'datepicker_nofuture');
		$("#TripEndDate").attr('class', 'datepicker');

		newrow = $("tr#new").clone();
		$("tr#new").removeAttr('id');
		$("#TripStartDate").parent().append("<span>"+S+"</span>");
		$("#TripStartDate").parent().append("<input type='hidden' name='TripStartDate:list' value='"+S+"'/>");
		$("#TripStartDate").remove();
		$("#TripEndDate").parent().append("<span>"+E+"</span>");
		$("#TripEndDate").parent().append("<input type='hidden' name='TripEndDate:list' value='"+E+"'/>");
		$("#TripEndDate").remove();
		$("#Country").parent().append("<span>"+T+"</span>");
		$("#Country").parent().append("<input type='hidden' name='Country:list' value='"+T+"'/>");
		$("#Country").remove();
		$("#Location").parent().append("<span>"+L+"</span>");
		$("#Location").parent().append("<input type='hidden' name='Location:list' value='"+L+"'/>");
		$("#Location").remove();
		for(i=0; i<$(newrow).children().length; i++){
			td = $(newrow).children()[i];
			input = $(td).children()[0];
			$(input).val('');
		}
		$(newrow).appendTo($(".bika-listing-table"));
		lookups();
		return false;
	})
});
}(jQuery));
