jQuery(function($){
	$(document).ready(function(){		
		
		// Only show Month of Pregnancy if Pregnant checked
		$("#MenstrualStatus-Pregnant-0").click(function() {
			if (!this.checked) {
				$("#MenstrualStatus-MonthOfPregnancy-0").val('');
				$("#MenstrualStatus-MonthOfPregnancy-0").parent().hide();
			} else {
				$("#MenstrualStatus-MonthOfPregnancy-0").parent().show();
				$("#MenstrualStatus-MonthOfPregnancy-0").focus()
			}
		});
		
		// Set Pregnant unchecked if no Month of pregnancy value entered
		$("#MenstrualStatus-MonthOfPregnancy-0").focusout(function() {
			if ($.trim($("#MenstrualStatus-MonthOfPregnancy-0").val()) == '') {
				$("#MenstrualStatus-Pregnant-0").attr('checked', false);
				$("#MenstrualStatus-MonthOfPregnancy-0").val('');
				$("#MenstrualStatus-MonthOfPregnancy-0").parent().hide();
			}
		});
		
		// The widget must only be shown if patient's gender is female
		if ($('#archetypes-fieldname-MenstrualStatus').length){
			gender = $("#MenstrualStatus-PatientGender").val();
			if (gender=='female') {
				$('#archetypes-fieldname-MenstrualStatus').show();								
			} else {
				$('#archetypes-fieldname-MenstrualStatus').hide();
			}
		}
	});
});