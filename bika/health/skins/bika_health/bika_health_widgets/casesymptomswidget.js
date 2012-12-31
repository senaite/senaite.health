jQuery(function($){
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');

    // Case Symptoms -> combined ICD9(R)/bika_symptoms lookup
    function loadSymptomsCombo(){
        $(".template-symptoms #Title").combogrid({
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

    	// When input receives focus, value must be reseted to empty and
    	// the popup must show all the items available
    	$(".template-symptoms #Title").focus(function(event){
        	$(".template-symptoms #Description").val('');
            $(".template-symptoms #Code").val('');
        	$(this).val('');
        });

    	// When symptom value changes it must be validated against ZopeDB
    	// If no exists, the code and description input elements will be setted
    	// up in editable mode, for further creation of the new Symptom
    	$(".template-symptoms #Title").change(function(event){
    		$.ajax({
                type: 'POST',
                url: window.portal_url + '/getSymptoms',
                data: {'_authenticator': $('input[name="_authenticator"]').val(),
                       'title': $(this).val()},
        		dataType: "json",
            	success: function(data, textStatus, $XHR){
            		if (data == null || data['rows'].length < 1) {
            			$(".template-symptoms #Code").attr('readonly', false);
            			$(".template-symptoms #Code").attr('disabled', false);
            			$(".template-symptoms #Description").attr('readonly', false);
            			$(".template-symptoms #Description").attr('disabled', false);
            			$(".template-symptoms #Description").focus();
            			$(".template-symptoms #add_row").removeAttr('disabled');
            		} else {
            			$(".template-symptoms #Code").attr('readonly', true);
            			$(".template-symptoms #Code").attr('disabled', true);
            			$(".template-symptoms #Description").attr('readonly', true);
            			$(".template-symptoms #Description").attr('disabled', true);
            			$(".template-symptoms #add_row").removeAttr('disabled');
            			$(".template-symptoms #SymptomOnset").focus();
            		}
    			},
    			error: function(){
    				//Error while searching
    				$(".template-symptoms #Code").attr('readonly', true);
        			$(".template-symptoms #Code").attr('disabled', true);
        			$(".template-symptoms #Description").attr('readonly', true);
        			$(".template-symptoms #Description").attr('disabled', true);
        			$(".template-symptoms #add_row").removeAttr('disabled');
        			$(".template-symptoms #SymptomOnset").focus();
    			}
            });
    	});

    	$(".template-symptoms #add_row").click(function(event){
            event.preventDefault();
            C = $(".template-symptoms #Code").val();
            T = $(".template-symptoms #Title").val();
            D = $(".template-symptoms #Description").val();
            O = $(".template-symptoms #SymptomOnset").val();
            if (T == ''){
                return false;
            }

         // Check if there's already an entry saved
            codrows = $("input[name='CSY_SCode:list']");
            for(i=0; i<codrows.length; i++){
            	code = codrows[i];
            	if (C==code.value) {
            		ct=$("input[name='CSY_STitle:list']")[i];
            		cd=$("input[name='CSY_SDescription:list']")[i];
            		co=$("input[name='CSY_SSymptomOnset:list']")[i];
            		if (ct.value==T && cd.value==D && co.value==O) {
            			alert(_('Symptom already added'));
            			$(".template-symptoms #Title").focus();
            			return false;
            		}
            	}
    		}

            // Check if there¡s already an entry added
            codrows = $("input[name='CSY_Code:list']");
            for(i=0; i<codrows.length; i++){
            	code = codrows[i];
            	if (C==code.value) {
            		ct=$("input[name='CSY_Title:list']")[i];
            		cd=$("input[name='CSY_Description:list']")[i];
            		co=$("input[name='CSY_SymptomOnset:list']")[i];
            		if (ct.value==T && cd.value==D && co.value==O) {
            			alert(_('Symptom already added'));
            			$(".template-symptoms #Title").focus();
            			return false;
            		}
            	}
    		}

            // Avoids datewidget unload after adding new row without postback
            $(".template-symptoms #SymptomOnset").attr('class', 'datepicker_nofuture');

            newrow = $(".template-symptoms tr#new").clone();
            $(".template-symptoms tr#new").removeAttr('id');
            $(".template-symptoms #Code").parent().append(C);
            $(".template-symptoms #Code").parent().append("<input type='hidden' name='CSY_Code:list' value='"+C+"'/>");
            $(".template-symptoms #Code").remove();
            $(".template-symptoms #Title").parent().append(T);
            $(".template-symptoms #Title").parent().append("<input type='hidden' name='CSY_Title:list' value='"+T+"'/>");
            $(".template-symptoms #Title").remove();
            $(".template-symptoms #Description").parent().append(D);
            $(".template-symptoms #Description").parent().append("<input type='hidden' name='CSY_Description:list' value='"+D+"'/>");
            $(".template-symptoms #Description").remove();
            $(".template-symptoms #SymptomOnset").parent().append(O);
            $(".template-symptoms #SymptomOnset").parent().append("<input type='hidden' name='CSY_SymptomOnset:list' value='"+O+"'/>");
            $(".template-symptoms #SymptomOnset").remove();
            for(i=0; i<$(newrow).children().length; i++){
                td = $(newrow).children()[i];
                input = $(td).children()[0];
                $(input).val('');
            }
            $(newrow).appendTo($(".template-symptoms .bika-listing-table"));
            load();
            return false;
        });

        loadSymptomsCombo();
    }

    load();

});
});
