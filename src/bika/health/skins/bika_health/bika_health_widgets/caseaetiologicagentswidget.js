jQuery(function($){
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');

    function loadAgentsCombo(){
        // Case Aetiologic Agents > Aetiologic Agent popup
        $(".template-caseaetiologicagents #Title").combogrid({
            colModel: [{'columnName':'Title', 'width':'30', 'label':_('Title')},
                       {'columnName':'Description', 'width':'70', 'label':_('Description')},
                       {'columnName':'AgentUID', 'hidden':true}],
            showOn: true,
            url: window.portal_url + "/getAetiologicAgents?_authenticator=" + $('input[name="_authenticator"]').val(),
            showOn: true,
            select: function( event, ui ) {
                event.preventDefault();
                $(this).val(ui.item.Title);
                $(this).parents('tr').find('input[id=Title]').val(ui.item.Title);
                $(this).parents('tr').find('input[id=Description]').val(ui.item.Description);
                $(this).parents('tr').find('input[id=AgentUID]').val(ui.item.AgentUID);
                $(this).change();
                return false;
            }
        });
    }

    function loadAgentSubtypesCombo() {
    	if ($(".template-caseaetiologicagents #Title").val() != '') {
	    	// Case Aetiologic Agents > Aetiologic agent row > Subtypes popup
	        // This combo depends on the selected Aetiologic agent in the previous one
    		auid = $('input[id=AgentUID]').val()
	        $(".template-caseaetiologicagents #Subtype").combogrid({
	        	colModel: [{'columnName':'Subtype', 'width':'30', 'label':_('Subtype')},
	                       {'columnName':'SubtypeRemarks', 'width':'70', 'label':_('SubtypeRemarks')}],
	            showOn: true,
	            url: window.portal_url + "/getAetiologicAgentSubtypes?_authenticator=" + $('input[name="_authenticator"]').val()+"&auid=" + auid,
	            select: function( event, ui ) {
	                event.preventDefault();
	                $(this).val(ui.item.Subtype);
	                $(this).parents('tr').find('input[id=Subtype]').val(ui.item.Subtype);
	                $(this).change();
	                return false;
	            }
	        });
			$(".template-caseaetiologicagents #Subtype").focus();
			$(".template-caseaetiologicagents #Subtype").attr('readonly', false);
			$(".template-caseaetiologicagents #Subtype").attr('disabled', false);
    	} else {
    		$(".template-caseaetiologicagents #Subtype").val('');
			$(".template-caseaetiologicagents #Subtype").attr('readonly', true);
			$(".template-caseaetiologicagents #Subtype").attr('disabled', true);
    	}
    }

    function load() {

    	// When input receives focus, value must be reseted to empty and
    	// the popup must show all the items available
    	$(".template-caseaetiologicagents #Title").focus(function(event){
        	$(".template-caseaetiologicagents #Description").val('');
            $(".template-caseaetiologicagents #AgentUID").val('');
        	$(this).val('');
        	loadAgentSubtypesCombo();
        });

    	// When aetiologic agent selected changes, the value must be validated
    	// against ZopeDB, cause no free text is allowed. The combo for
    	// aetiologic agent subtypes will be also loaded in accordance
    	// to the aetiologic agent.
    	$(".template-caseaetiologicagents #Title").change(function(event){
        	$.ajax({
                type: 'POST',
                url: window.portal_url + '/getAetiologicAgents',
                data: {'_authenticator': $('input[name="_authenticator"]').val(),
                       'title': $(this).val()},
        		dataType: "json",
            	success: function(data, textStatus, $XHR){
            		if (data == null || data['rows'].length < 1) {
            			//Aetiologic agent doesn't exist
            			$(".template-caseaetiologicagents #Title").focus();
            		}
    			},
    			error: function(){
    				//Error while searching for aetiologic agent
        			$(".template-caseaetiologicagents #Title").focus();
    			}
            });
        	loadAgentSubtypesCombo();
        });

    	// When subtype value changes it must be validated against ZopeDB
    	// (no free text allowed). If no exists, the input element will be
    	// reseted to empty
        $(".template-caseaetiologicagents #Subtype").change(function(event){
        	$.ajax({
                type: 'POST',
                url: window.portal_url + '/getAetiologicAgentSubtypes',
                data: {'_authenticator': $('input[name="_authenticator"]').val(),
                       'title': $(this).val(),
                       'auid':$(".template-caseaetiologicagents #AgentUID").val()},
        		dataType: "json",
            	success: function(data, textStatus, $XHR){
            		if (data == null || data['rows'].length < 1) {
            			//Subtype doesn't exist
            			$(".template-caseaetiologicagents #Subtype").val('');
            			$(".template-caseaetiologicagents #Subtype").focus();
            			return false;
            		} else {
            			$(".template-caseaetiologicagents .add_row").removeAttr('disabled');
            		}
    			},
    			error: function(){
    				//Error while searching
        			$(".template-caseaetiologicagents #Subtype").val('');
        			$(".template-caseaetiologicagents #Subtype").focus();
        			$(".template-caseaetiologicagents #add_row").removeAttr('disabled');
        			return false;
    			}
            });
        });

        $(".template-caseaetiologicagents #add_row").click(function(event){
            event.preventDefault();
            T = $(".template-caseaetiologicagents #Title").val();
            D = $(".template-caseaetiologicagents #Description").val();
            S = $(".template-caseaetiologicagents #Subtype").val();
            I = $(".template-caseaetiologicagents #AgentUID").val();
            if (T == ''){
                return false;
            }

            // Check if case has already saved the entry
            titrows = $("input[name='CAE_STitle:list']");
            for(i=0; i<titrows.length; i++){
            	title = titrows[i];
            	if (T==title.value) {
            		str=$("input[name='CAE_SSubtype:list']")[i];
            		if (str.value==S) {
            			alert(_('Aetiologic agent already added'));
            			$(".template-caseaetiologicagents #Subtype").val('');
            			$(".template-caseaetiologicagents #Subtype").focus();
            			return false;
            		}
            	}
    		}
            // Check if entry has already been added
            titrows = $("input[name='CAE_Title:list']");
            for(i=0; i<titrows.length; i++){
            	title = titrows[i];
            	if (T==title.value) {
            		str=$("input[name='CAE_Subtype:list']")[i];
            		if (str.value==S) {
            			alert(_('Aetiologic agent already added'));
            			$(".template-caseaetiologicagents #Subtype").val('');
            			$(".template-caseaetiologicagents #Subtype").focus();
            			return false;
            		}
            	}
    		}

            // Add the new row
            newrow = $(".template-caseaetiologicagents tr#new").clone();
            $(".template-caseaetiologicagents tr#new").removeAttr('id');
            $(".template-caseaetiologicagents #Title").parent().append(T);
            $(".template-caseaetiologicagents #Title").parent().append("<input type='hidden' name='CAE_Title:list' value='"+T+"'/>");
            $(".template-caseaetiologicagents #Title").remove();
            $(".template-caseaetiologicagents #AgentUID").parent().append("<input type='hidden' name='CAE_AgentUID:list' value='"+I+"'/>");
            $(".template-caseaetiologicagents #AgentUID").remove();
            $(".template-caseaetiologicagents #Description").parent().append(D);
            $(".template-caseaetiologicagents #Description").parent().append("<input type='hidden' name='CAE_Description:list' value='"+D+"'/>");
            $(".template-caseaetiologicagents #Description").remove();
            $(".template-caseaetiologicagents #Subtype").parent().append(S);
            $(".template-caseaetiologicagents #Subtype").parent().append("<input type='hidden' name='CAE_Subtype:list' value='"+S+"'/>");
            $(".template-caseaetiologicagents #Subtype").remove();
            for(i=0; i<$(newrow).children().length; i++){
                td = $(newrow).children()[i];
                input = $(td).children()[0];
                $(input).val('');
            }
            $(newrow).appendTo($(".template-caseaetiologicagents .bika-listing-table"));
            load();
            return false;
        });

        loadAgentsCombo();
        loadAgentSubtypesCombo();
    }

    load();

});
});
