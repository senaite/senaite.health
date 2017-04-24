# This file is part of Bika Health
#
# Copyright 2011-2017 by its authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.health import logger
from bika.health.upgrade import upgradestep
from bika.health.upgrade.utils import UpgradeUtils
from bika.health.catalog.patient_catalog import CATALOG_PATIENT_LISTING
import traceback
import sys
import transaction

product = 'bika.health'
version = '3.2.0.1704'


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    ut = UpgradeUtils(portal)
    ufrom = ut.getInstalledVersion(product)
    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
                    product, ufrom, version))
        # The currently installed version is more recent than the target
        # version of this upgradestep
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ufrom, version))

    addSearchableTextIndex(portal, CATALOG_PATIENT_LISTING)

    # Refresh affected catalogs
    ut.refreshCatalogs()

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def addSearchableTextIndex(portal, catalog):
    # Create lexicon to be able to add ZCTextIndex
    wordSplitter = Empty()
    wordSplitter.group = 'Word Splitter'
    wordSplitter.name = 'Unicode Whitespace splitter'
    caseNormalizer = Empty()
    caseNormalizer.group = 'Case Normalizer'
    caseNormalizer.name = 'Unicode Case Normalizer'
    stopWords = Empty()
    stopWords.group = 'Stop Words'
    stopWords.name = 'Remove listed and single char words'
    elem = [wordSplitter, caseNormalizer, stopWords]
    zc_extras = Empty()
    zc_extras.index_type = 'Okapi BM25 Rank'
    zc_extras.lexicon_id = 'Lexicon'

    cat = getToolByName(portal, catalog, None)
    if cat is None:
        logger.warning('Could not find the catalog tool.' + catalog)
        return

    try:
        cat.manage_addProduct['ZCTextIndex'].manage_addLexicon('Lexicon',
                                                               'Lexicon', elem)
    except:
        logger.warning('Could not add ZCTextIndex to '+catalog)
        pass

    addIndex(cat, 'SearchableText', 'ZCTextIndex', zc_extras)


def addIndex(cat, *args):
    try:
        cat.addIndex(*args)
    except:
        pass


class Empty:
    pass
