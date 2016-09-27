# This file is part of Bika Health LIS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.health import logger
from Products.CMFCore import permissions


def upgrade(tool):
    """Upgrade step required for Bika Health 3.2.0
    """
    portal = aq_parent(aq_inner(tool))

    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo('bika.health')['installedVersion']
    logger.info("Upgrading Bika Health: %s -> %s" % (ufrom, '3.1.8'))

    """Updated profile steps
    list of the generic setup import step names: portal.portal_setup.getSortedImportSteps() <---
    if you want more metadata use this: portal.portal_setup.getImportStepMetadata('jsregistry') <---
    important info about upgrade steps in
    http://stackoverflow.com/questions/7821498/is-there-a-good-reference-list-for-the-names-of-the-genericsetup-import-steps
    """
    setup = portal.portal_setup
    # setup.runImportStepFromProfile('profile-bika.health:default', 'typeinfo')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'jsregistry')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'cssregistry')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'workflow-csv')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'factorytool')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'controlpanel')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'catalog')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'propertiestool')
    # setup.runImportStepFromProfile('profile-bika.health:default', 'skins')
    """Update workflow permissions
    """
    # wf = getToolByName(portal, 'portal_workflow')
    # wf.updateRoleMappings()
    return True
