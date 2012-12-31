## Script (Python) "validate_integrity"
##title=Validate Integrity
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##

from Products.Archetypes import PloneMessageFactory as _
from Products.Archetypes.utils import addStatusMessage

request = context.REQUEST
errors = {}
errors = context.validate(REQUEST=request, errors=errors, data=1, metadata=0)

if errors:
    message = _(u'Please correct the indicated errors.')
    addStatusMessage(request, message, type='error')
    return state.set(status='failure', errors=errors)
else:
    message = _(u'Changes saved.')
    stat = 'created'
    
    # Redirection after saving edition forms      
    if context.portal_type == 'AetiologicAgent':
    	state.setNextAction('redirect_to:string:${portal_url}/bika_setup/bika_aetiologicagents')
    	
    elif context.portal_type == 'BatchLabel':
    	state.setNextAction('redirect_to:string:${portal_url}/bika_setup/bika_batchlabels')
    
    elif context.portal_type == 'CaseOutcome':
    	state.setNextAction('redirect_to:string:${portal_url}/bika_setup/bika_caseoutcomes')
    	
    elif context.portal_type == 'CaseStatus':
    	state.setNextAction('redirect_to:string:${portal_url}/bika_setup/bika_casestatuses')
    
    elif context.portal_type == 'Disease':
    	state.setNextAction('redirect_to:string:${portal_url}/bika_setup/bika_diseases')
    	
    elif context.portal_type == 'Drug':
    	state.setNextAction('redirect_to:string:${portal_url}/bika_setup/bika_drugs')
    
    elif context.portal_type == 'DrugProhibition':
    	state.setNextAction('redirect_to:string:${portal_url}/bika_setup/bika_drugprohibitions')
    	
    elif context.portal_type == 'Immunization':
    	state.setNextAction('redirect_to:string:${portal_url}/bika_setup/bika_immunizations')
    
    elif context.portal_type == 'SampleOrigin':
        state.setNextAction('redirect_to:string:${portal_url}/bika_setup/bika_sampleorigins')
    	
    elif context.portal_type == 'Treatment':
    	state.setNextAction('redirect_to:string:${portal_url}/bika_setup/bika_treatments')
    	
    elif context.portal_type == 'VaccionationCenter':
    	state.setNextAction('redirect_to:string:${portal_url}/bika_setup/bika_vaccionationcenters')
    	
    elif context.portal_type == 'EpidemiologicalYear':
    	state.setNextAction('redirect_to:string:${portal_url}/bika_setup/bika_epidemiologicalyears')
    
    elif context.portal_type == 'IdentifierType':
    	state.setNextAction('redirect_to:string:${portal_url}/bika_setup/bika_identifiertypes')
    
    else:
    	stat = 'success'
    	
	addStatusMessage(request, message)
    return state.set(status=stat)
