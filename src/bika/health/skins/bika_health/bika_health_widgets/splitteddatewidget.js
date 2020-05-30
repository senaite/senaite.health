jQuery( function($) {
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');

    fieldName = $('fieldName').val();
	yearField = $(fieldName + "_year");
	monthField = $(fieldName + "_month");
	dayField = $(fieldName + "_day");

	now = new Date();
	currentyear = now.getFullYear();
	currentmonth = now.getMonth();
	currentday = now.getDay();

	function isValidDate() {
		year = yearField.val();
		month = monthField.val();
		day = dayField.val();

		//TODO: Check if valid date

		return true;
	}

	yearField.live('change', function(){
		if (!isValidDate()) {
			yearField.value('');
		}
	});

	monthField.live('change', function(){
		if (!isValidDate()) {
			monthField.value('');
		}
	});

	dayField.live('change', function(){
		if (!isValidDate()) {
			dayField.value('');
		}
	});
});
});
