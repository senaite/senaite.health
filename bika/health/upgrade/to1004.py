from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """ Reset Patient and Doctor in ARs created from Cases
    """
    portal = aq_parent(aq_inner(tool))
    pc = getToolByName(portal, 'portal_catalog')
    bpc = getToolByName(portal, 'bika_patient_catalog')
    proxies = pc(portal_type="AnalysisRequest")
    ars = (proxy.getObject() for proxy in proxies)
    for ar in ars:
        batch = ar.getBatch()
        if batch:
            patient = batch['PatientID']
            if patient:
                pat = bpc(portal_type='Patient', id=patient)
                if pat:
                    try:
                        ar.Schema().getField('Patient').set(ar,pat[0]['UID'])
                    except:
                        pass

            doctor = batch['DoctorID']
            if doctor:
                doc = pc(portal_type="Doctor", getDoctorID=doctor)
                if doc:
                    try:
                        ar.Schema().getField('Doctor').set(ar, doc[0]['UID'])
                    except:
                        pass

    return True
