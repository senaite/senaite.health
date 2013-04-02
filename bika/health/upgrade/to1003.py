from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """ Just some catalog indexes to update
    """
    portal = aq_parent(aq_inner(tool))
    portal_catalog = getToolByName(portal, 'portal_catalog')
    bikasetup = portal['bika_setup']
    proxies = portal_catalog(portal_type="Batch")
    batches = (proxy.getObject() for proxy in proxies)
    for batch in batches:
        oldcond = len(batch.getPatientCondition()) > 0 \
                    and batch.getPatientCondition() \
                    or []

        newrows = []
        for i in range(len(oldcond)):
            oldheight = oldcond[i].get('Height', '')
            oldweight = oldcond[i].get('Weight', '')
            oldwaist = oldcond[i].get('Waist', '')

            if oldheight or oldweight or oldwaist:
                heunit = bikasetup.getPatientConditionsHeightUnits()
                heunit = (heunit and "/" in heunit) and heunit.split('/') or [heunit]
                weunit = bikasetup.getPatientConditionsWeightUnits()
                weunit = (weunit and "/" in weunit) and weunit.split('/') or [weunit]
                waunit = bikasetup.getPatientConditionsWaistUnits()
                waunit = (waunit and "/" in waunit) and waunit.split('/') or [waunit]
                newrows.append({'Condition':'Height',
                                'Unit': (heunit and len(heunit) > 0) and heunit[0] or '',
                                'Value': oldheight})
                newrows.append({'Condition':'Weight',
                                'Unit': (weunit and len(weunit) > 0) and weunit[0] or '',
                                'Value': oldweight})
                newrows.append({'Condition':'Waist',
                                'Unit': (waunit and len(waunit) > 0) and waunit[0] or '',
                                'Value': oldwaist})

        batch.setPatientCondition(newrows)

    return True
