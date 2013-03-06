jQuery(function($){
	$(document).ready(function(){
		
		radios = $("#Symptoms_table input:radio");
		for (i=0; i<radios.length; i++) {
			$("#Symptoms_table #"+radios[i].id).click(function() {
				idx = this.id.split("-")[2];
				$("#Symptoms_table #Symptoms-Selected-"+idx).attr('checked', true);
				$("#Symptoms_table #Symptoms-Assigned-"+idx).val(1);
			});
		}		
		
		symptoms = $("#Symptoms_table input:checkbox");
		for (i=0; i<symptoms.length; i++) {
			$("#Symptoms_table #"+symptoms[i].id).click(function() {
				idx = this.id.split("-")[2];
				if (!this.checked) {
					$("#Symptoms_table #Symptoms-Severity-"+idx).attr('checked', false);
					$("#Symptoms_table #Symptoms-Assigned-"+idx).val(0);
				} else {
					$("#Symptoms_table #Symptoms-Severity-"+idx+":radio").attr('checked', true);
					$("#Symptoms_table #Symptoms-Assigned-"+idx).val(1);
				}
			});
		}	
		
		$("#Symptoms_table tr:even").css("background-color", "#efefef");
	});
});