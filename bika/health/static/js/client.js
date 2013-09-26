(function( $ ) {
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');

    // Confirm before resetting client specs to default lab specs
    $("a[href*=set_to_lab_defaults]").click(function(event){
        // always prevent default/
        // url is activated manually from 'Yes' below.
        url = $(this).attr("href");
        event.preventDefault();
        yes = _('Yes');
        no = _('No');
        var $confirmation = $("<div></div>")
            .html(_("This will remove all existing client analysis specifications "+
                    "and create copies of all lab specifications. "+
                    "Are you sure you want to do this?"))
            .dialog({
                resizable:false,
                title: _('Set to lab defaults'),
                buttons: {
                    yes: function(event){
                        $(this).dialog("close");
                        window.location.href = url;
                    },
                    no: function(event){
                        $(this).dialog("close");
                    }
                }
            });
    });

    $("input[id=Client]").combogrid({
        colModel: [{'columnName':'ClientUID','hidden':true},
                   {'columnName':'ClientID','width':'20','label':_('Client ID')},
                   {'columnName':'Title','width':'80','label':_('Title')}],
        showOn: true,
        width: '450px',
        url: window.portal_url + "/getClients?_authenticator=" + $('input[name="_authenticator"]').val(),
        showOn: true,
        select: function( event, ui ) {
            $(this).val(ui.item.ClientID);
            $(this).change();
            if($(".portaltype-batch").length > 0 && $(".template-base_edit").length > 0) {
                $(".jsClientTitle").remove();
                $("#archetypes-fieldname-Client").append("<span class='jsClientTitle'>"+ui.item.Title+"</span>");
            }
            return false;
        }
    });

});
}(jQuery));
