jQuery(function($){
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');

    function lookups(){

        // Patient identifiers > Identifier Types popup
        $(".template-patientidentifiers #IdentifierType").combogrid({
            colModel: [{'columnName':'UID', 'hidden':true},
                       {'columnName':'Title', 'width':'30', 'label':_('Title')},
                       {'columnName':'Description', 'width':'70', 'label':_('Description')}],
            url: window.portal_url + "/getIdentifierTypes?_authenticator=" + $('input[name="_authenticator"]').val(),
            showOn: true,
            select: function( event, ui ) {
                event.preventDefault();
                $(this).val(ui.item.Title);
                $(this).parents('tr').find('input[id=IdentifierType]').val(ui.item.Title);
                $(this).parents('tr').find('input[id=IdentifierTypeUID]').val(ui.item.UID);
                $(this).parents('tr').find('input[id=IdentifierTypeDescription]').val(ui.item.Description);
                $(this).change();
                return false;
            }
        });
    }
    lookups();

    $(".template-patientidentifiers .add_row").click(function(event){
        event.preventDefault();
        U = $(".template-patientidentifiers #IdentifierTypeUID").val();
        T = $(".template-patientidentifiers #IdentifierType").val();
        D = $(".template-patientidentifiers #IdentifierTypeDescription").val();
        I = $(".template-patientidentifiers #Identifier").val();
        /*if (T == ''){
        	alert(_("No Identifier Type defined"))
            return false;
        } else */ if (I == '') {
        	alert(_("No Identifier entered"))
        	return false;
        }

        newrow = $(".template-patientidentifiers tr#new").clone();
        $(".template-patientidentifiers tr#new").removeAttr('id');
        $(".template-patientidentifiers #IdentifierTypeUID").parent().append("<input type='hidden' name='PID_IdentifierTypeUID:list' value='"+U+"'/>");
        $(".template-patientidentifiers #IdentifierTypeUID").remove();
        $(".template-patientidentifiers #IdentifierType").parent().append("<span>"+T+"</span>");
        $(".template-patientidentifiers #IdentifierType").parent().append("<input type='hidden' name='PID_IdentifierType:list' value='"+T+"'/>");
        $(".template-patientidentifiers #IdentifierType").remove();
        $(".template-patientidentifiers #IdentifierTypeDescription").parent().append("<span>"+D+"</span>");
        $(".template-patientidentifiers #IdentifierTypeDescription").parent().append("<input type='hidden' name='PID_IdentifierTypeDescription:list' value='"+D+"'/>");
        $(".template-patientidentifiers #IdentifierTypeDescription").remove();
        $(".template-patientidentifiers #Identifier").parent().append("<span>"+I+"</span>");
        $(".template-patientidentifiers #Identifier").parent().append("<input type='hidden' name='PID_Identifier:list' value='"+I+"'/>");
        $(".template-patientidentifiers #Identifier").remove();
        for(i=0; i<$(newrow).children().length; i++){
            td = $(newrow).children()[i];
            input = $(td).children()[0];
            $(input).val('');
        }
        $(newrow).appendTo($(".template-patientidentifiers .bika-listing-table"));
        lookups();
        return false;
    })

});
});
