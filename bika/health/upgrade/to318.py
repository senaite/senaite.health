from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.utils import tmpID
from bika.lims.idserver import renameAfterCreation
from bika.health.permissions import AddEthnicity, ViewEthnicities
from bika.lims import logger


def upgrade(tool):

    # Adding bika.health.analysisrequest.ar_add_health_standard.js
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo('bika.health')['installedVersion']    
    logger.info("Upgrading Bika Health: %s -> %s" % (ufrom, '318'))


    return True
