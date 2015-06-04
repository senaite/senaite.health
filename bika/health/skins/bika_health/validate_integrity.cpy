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
    redirects = {'AetiologicAgent' : '/bika_setup/bika_aetiologicagents',
                 'BatchLabel' : '/bika_setup/bika_batchlabels',
                 'CaseOutcome': '/bika_setup/bika_caseoutcomes',
                 'CaseSyndromicClassification' : '/bika_setup/bika_casesyndromicclassifications',
                 'CaseStatus': '/bika_setup/bika_casestatuses',
                 'Disease': '/bika_setup/bika_diseases',
                 'Drug': '/bika_setup/bika_drugs',
                 'DrugProhibition': '/bika_setup/bika_drugprohibitions',
                 'Immunization': '/bika_setup/bika_immunizations',
                 'Treatment': '/bika_setup/bika_treatments',
                 'VaccionationCenter': '/bika_setup/bika_vaccionationcenters',
                 'InsuranceCompany':  '/bika_setup/bika_insurancecompanies',
                 'EpidemiologicalYear': '/bika_setup/bika_epidemiologicalyears',
                 'IdentifierType': '/bika_setup/bika_identifiertypes',
                 'Symptom': '/bika_setup/bika_symptoms'}

    if context.portal_type in redirects:
        redirect = 'redirect_to:string:${portal_url}' + redirects[context.portal_type]
        state.setNextAction(redirect)
    else:
        stat = 'success'

    addStatusMessage(request, message)
    return state.set(status=stat)
