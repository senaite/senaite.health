from Acquisition import aq_inner
from Acquisition import aq_parent

def upgrade(tool):
    """Reorder invoices and ARimports in the navigation bar.
    """
    portal = aq_parent(aq_inner(tool))
    portal.moveObjectToPosition('invoices', portal.objectIds().index('supplyorders'))
    portal.moveObjectToPosition('arimports', portal.objectIds().index('referencesamples'))

    return True
