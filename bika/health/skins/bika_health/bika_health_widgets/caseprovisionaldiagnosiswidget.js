jQuery(function($){
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');

    // Case Symptoms -> combined ICD9(R)/bika_symptoms lookup
    function loadSymptomsCombo(){
        $(".template-caseprovisionaldiagnosis #Title").combogrid({
            colModel: [{'columnName':'Code', 'width':'10', 'label':_('Code')},
                       {'columnName':'Title', 'width':'25', 'label':_('Title')},
                       {'columnName':'Description', 'width':'65', 'label':_('Description')}],
            url: window.portal_url + "/getSymptoms?_authenticator=" + $('input[name="_authenticator"]').val(),
            showOn: true,
            select: function( event, ui ) {
                event.preventDefault();
                $(this).val(ui.item.Title);
                $(this).parents('tr').find('input[id=Code]').val(ui.item.Code);
                $(this).parents('tr').find('input[id=Description]').val(ui.item.Description);
                $(this).change();
                return false;
            }
        });
    }

    function load() {

    	$(".template-caseprovisionaldiagnosis #Code").attr('readonly', true);
		$(".template-caseprovisionaldiagnosis #Code").attr('disabled', true);
		$(".template-caseprovisionaldiagnosis #Description").attr('readonly', true);
		$(".template-caseprovisionaldiagnosis #Description").attr('disabled', true);
		$(".template-caseprovisionaldiagnosis #add_row").attr('disabled', true);

    	$(".template-caseprovisionaldiagnosis #Title").focus(function(event){
        	$(".template-caseprovisionaldiagnosis #Code").val('');
            $(".template-caseprovisionaldiagnosis #Description").val('');
        	$(this).val('');
        });

    	// When symptom value changes it must be validated against ZopeDB
    	// If no exists, the code and description input elements will be setted
    	// up in editable mode, for further creation of the new Symptom
    	$(".template-caseprovisionaldiagnosis #Title").change(function(event){
    		$.ajax({
                type: 'POST',
                url: window.portal_url + '/getSymptoms',
                data: {'_authenticator': $('input[name="_authenticator"]').val(),
                       'title': $(this).val()},
        		dataType: "json",
            	success: function(data, textStatus, $XHR){
            		if (data == null || data['rows'].length < 1) {
            			$(".template-caseprovisionaldiagnosis #Code").attr('readonly', false);
            			$(".template-caseprovisionaldiagnosis #Code").attr('disabled', false);
            			$(".template-caseprovisionaldiagnosis #Description").attr('readonly', false);
            			$(".template-caseprovisionaldiagnosis #Description").attr('disabled', false);
            			$(".template-caseprovisionaldiagnosis #Description").focus();
            			$(".template-caseprovisionaldiagnosis #add_row").removeAttr('disabled');
            		} else {
            			$(".template-caseprovisionaldiagnosis #Code").attr('readonly', true);
            			$(".template-caseprovisionaldiagnosis #Code").attr('disabled', true);
            			$(".template-caseprovisionaldiagnosis #Description").attr('readonly', true);
            			$(".template-caseprovisionaldiagnosis #Description").attr('disabled', true);
            			$(".template-caseprovisionaldiagnosis #add_row").removeAttr('disabled');
            			$(".template-caseprovisionaldiagnosis #Onset").focus();
            		}
    			},
    			error: function(){
    				//Error while searching
    				$(".template-caseprovisionaldiagnosis #Code").attr('readonly', true);
        			$(".template-caseprovisionaldiagnosis #Code").attr('disabled', true);
        			$(".template-caseprovisionaldiagnosis #Description").attr('readonly', true);
        			$(".template-caseprovisionaldiagnosis #Description").attr('disabled', true);
        			$(".template-caseprovisionaldiagnosis #add_row").removeAttr('disabled');
        			$(".template-caseprovisionaldiagnosis #Onset").focus();
    			}
            });
    	});

	    $(".template-caseprovisionaldiagnosis #add_row").click(function(event){
	        event.preventDefault();
	        C = $(".template-caseprovisionaldiagnosis #Code").val();
	        T = $(".template-caseprovisionaldiagnosis #Title").val();
	        D = $(".template-caseprovisionaldiagnosis #Description").val();
	        O = $(".template-caseprovisionaldiagnosis #Onset").val();
	        if (T == ''){
	            return false;
	        }

	        // Check if there's already an entry saved
            codrows = $("input[name='CPD_SCode:list']");
            for(i=0; i<codrows.length; i++){
            	code = codrows[i];
            	if (C==code.value) {
            		ct=$("input[name='CPD_STitle:list']")[i];
            		cd=$("input[name='CPD_SDescription:list']")[i];
            		co=$("input[name='CPD_SOnset:list']")[i];
            		if (ct.value==T && cd.value==D && co.value==O) {
            			alert(_('Provisional diagnosis already added'));
            			$(".template-caseprovisionaldiagnosis #Title").focus();
            			return false;
            		}
            	}
    		}

            // Check if there¡s already an entry added
            codrows = $("input[name='CPD_Code:list']");
            for(i=0; i<codrows.length; i++){
            	code = codrows[i];
            	if (C==code.value) {
            		ct=$("input[name='CPD_Title:list']")[i];
            		cd=$("input[name='CPD_Description:list']")[i];
            		co=$("input[name='CPD_Onset:list']")[i];
            		if (ct.value==T && cd.value==D && co.value==O) {
            			alert(_('Provisional diagnosis already added'));
            			$(".template-caseprovisionaldiagnosis #Title").focus();
            			return false;
            		}
            	}
    		}

	        // Avoids datewidget unload after adding new row without postback
	        $(".template-caseprovisionaldiagnosis #Onset").attr('class', 'datepicker_nofuture');

	        newrow = $(".template-caseprovisionaldiagnosis tr#new").clone();
	        $(".template-caseprovisionaldiagnosis tr#new").removeAttr('id');
	        $(".template-caseprovisionaldiagnosis #Code").parent().append(C);
	        $(".template-caseprovisionaldiagnosis #Code").parent().append("<input type='hidden' name='CPD_Code:list' value='"+C+"'/>");
	        $(".template-caseprovisionaldiagnosis #Code").remove();
	        $(".template-caseprovisionaldiagnosis #Title").parent().append(T);
	        $(".template-caseprovisionaldiagnosis #Title").parent().append("<input type='hidden' name='CPD_Title:list' value='"+T+"'/>");
	        $(".template-caseprovisionaldiagnosis #Title").remove();
	        $(".template-caseprovisionaldiagnosis #Description").parent().append(D);
	        $(".template-caseprovisionaldiagnosis #Description").parent().append("<input type='hidden' name='CPD_Description:list' value='"+D+"'/>");
	        $(".template-caseprovisionaldiagnosis #Description").remove();
	        $(".template-caseprovisionaldiagnosis #Onset").parent().append(O);
	        $(".template-caseprovisionaldiagnosis #Onset").parent().append("<input type='hidden' name='CPD_Onset:list' value='"+O+"'/>");
	        $(".template-caseprovisionaldiagnosis #Onset").remove();
	        for(i=0; i<$(newrow).children().length; i++){
	            td = $(newrow).children()[i];
	            input = $(td).children()[0];
	            $(input).val('');
	        }
	        $(newrow).appendTo($(".template-caseprovisionaldiagnosis .bika-listing-table"));
	        load();
	        return false;
	    });

	    loadSymptomsCombo();
    }

    load();

});
});
