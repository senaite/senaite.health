(function( $ ) {
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');
    
	// Analysis Service popup trigger    
	$("#email_popup").click(function(event){
		event.preventDefault();
		var dialog = $('<div></div>');
		dialog
			.load(window.portal_url + "/email_popup",
				{'uid':$('input[name="email_popup_uid"]').val(),
				 '_authenticator': $('input[name="_authenticator"]').val()}
			)
			.dialog({
				width:450,
				height:450,
				closeText: _("Close"),
				resizable:true,
				title: "<img src='" + window.portal_url + "/++resource++bika.lims.images/email.png'/>&nbsp;" + $(this).text()
			});
	});
	
	if ($('#email_popup').length) {
		if ($('input[name="email_popup_uid"]').attr('autoshow')=='True') {
			$('#email_popup').click();
		}
	}
	
	/* #HACK
	 * https://github.com/bikalabs/Bika-LIMS/issues/928
	 * Tricky and foolish stuff to override the hazardous icon in health.
	 * Seems that image resources override doesn't work in overrides.zcml
	 * (see bika/health/overrides.zcml and bika/health/static/overrides.zcml)
	 */
	$("img[src$='bika.lims.images/hazardous.png']").attr('src', window.portal_url + "/++resource++bika.health.images/hazardous.png");
	$("img[src$='bika.lims.images/hazardous_big.png']").attr('src', window.portal_url + "/++resource++bika.health.images/hazardous_big.png");
});
}(jQuery));

function addJavascript(jsname) {
	var th = document.getElementsByTagName('head')[0];
	var s = document.createElement('script');
	s.setAttribute('type','text/javascript');
	s.setAttribute('src',jsname);
	th.appendChild(s);
}

/**
 * Returns a GUID compliant with rfc4122 version 4
 */
function guid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
        return v.toString(16);
    });
}
