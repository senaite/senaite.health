jQuery(function($){
	$(document).ready(function(){	
		
		function loadOvariesRemoved() {
			if (!$("#MenstrualStatus-OvariesRemoved-0").attr('checked')) {
				$("#MenstrualStatus-OvariesRemovedNum-0:radio").attr('checked', false);
				$("#MenstrualStatus-OvariesRemovedYear-0").val('');
				$("#MenstrualStatus-OvariesRemovedYear-0").parent().hide();
			} else {
				$("#MenstrualStatus-OvariesRemovedNum-0:radio").attr('checked', true);
				$("#MenstrualStatus-OvariesRemovedYear-0").parent().show();
				$("#MenstrualStatus-OvariesRemovedYear-0").focus()
			}
		}
		
		function loadHysterectomy() {
			if (!$("#MenstrualStatus-Hysterectomy-0").attr('checked')) {
				$("#MenstrualStatus-HysterectomyYear-0").val('');
				$("#MenstrualStatus-HysterectomyYear-0").parent().hide();
			} else {
				$("#MenstrualStatus-HysterectomyYear-0").parent().show();
				$("#MenstrualStatus-HysterectomyYear-0").focus()
			}
		}
		
		// Only show Hysterectomy year if Hysterectomy checked
		$("#MenstrualStatus-Hysterectomy-0").click(function() {
			loadHysterectomy();
		});
		
		// Only show Ovaries removed num & year if Ovaries Removed checked
		$("#MenstrualStatus-OvariesRemoved-0").click(function() {
			loadOvariesRemoved();			
		});
		
		// Set Hysterectomy unchecked if no year of Hysterectomy value entered
		$("#MenstrualStatus-HysterectomyYear-0").focusout(function() {
			if ($.trim($("#MenstrualStatus-HysterectomyYear-0").val()) == '') {
				$("#MenstrualStatus-Hysterectomy-0").attr('checked', false);
				$("#MenstrualStatus-HysterectomyYear-0").val('');
				$("#MenstrualStatus-HysterectomyYear-0").parent().hide();
			}
		});
		
		// Set Ovaries removed unchecked if no year of ovaries removed year value entered
		/*$("#MenstrualStatus-OvariesRemovedYear-0").focusout(function() {
			if ($.trim($("#MenstrualStatus-OvariesRemovedYear-0").val()) == '') {
				$("#MenstrualStatus-OvariesRemoved-0").attr('checked', false);
				$("#MenstrualStatus-OvariesRemovedYear-0").val('');
				$("#MenstrualStatus-OvariesRemovedYear-0").parent().hide();
			}
		});*/
		
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