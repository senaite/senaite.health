(function( $ ) {
$(document).ready(function(){

    _p = jarn.i18n.MessageFactory('plone');
    _b = jarn.i18n.MessageFactory('bika');
    _ = jarn.i18n.MessageFactory('bika.health');
    
	// Analysis Service popup trigger    
	$("#email_popup").live('click', function(){
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
	
});
}(jQuery));

function addJavascript(jsname) {
	var th = document.getElementsByTagName('head')[0];
	var s = document.createElement('script');
	s.setAttribute('type','text/javascript');
	s.setAttribute('src',jsname);
	th.appendChild(s);
}