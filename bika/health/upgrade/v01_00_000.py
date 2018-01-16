# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Acquisition import aq_inner
from Acquisition import aq_parent

import transaction

from bika.health import logger
from bika.health.config import PROJECTNAME as product
from bika.lims.api import get_object
from bika.lims.api import get_schema
from bika.lims.api import get_tool
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.0.0'
profile = 'profile-{0}:default'.format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    # Since this upgrade is precisely meant to establish a version regardless
    # of the version numbering at bikalims/bika.health, we don't want this check
    # to be performed.
    # if ut.isOlderVersion(product, version):
    #    logger.info("Skipping upgrade of {0}: {1} > {2}".format(
    #        product, ufrom, version))
    #    # The currently installed version is more recent than the target
    #    # version of this upgradestep
    #    return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.health:default', 'jsregistry')
    # Do nothing, we just only want the profile version to be 1.0.0

    update_ar_proxyfields(portal)
    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def update_ar_proxyfields(portal):
    """
    Some AnalysisRequest fields have become ProxyFields of Sample, so we need
    to update them in order port those values to Sample objects aswell.
    :param portal: Plone portal object
    :return: True if success, False otherwise
    """
    logger.info(
        "'Patient' and 'ClientPatientID' fields from all Analysis "
        "Request objects will be 'get' and 'set' in order to update its "
        "proxies")
    all_ok = True
    ar_catalog = get_tool(CATALOG_ANALYSIS_REQUEST_LISTING, context=portal)
    all_ars = ar_catalog()
    processed = 0
    total = len(all_ars)
    logger.info('{} Analysis Request objects to process...'.format(total))

    # Go over all Analysis Requests
    for ar_brain in all_ars:
        # getting object
        ar_obj = get_object(ar_brain)
        clientpatientid_it_work = clientpatientid_from_ar_to_sample(ar_obj)

        # Updating ClientPatientID field
        if not clientpatientid_it_work:
            logger.warn(
                "ClientPatientID Field for Analysis Request '{}' could not "
                "be updated.".format(ar_obj.getId()))
            all_ok = False

        # Updating Patient field
        patient_it_work = patient_from_ar_to_sample(ar_obj)
        if not patient_it_work:
            logger.warn(
                "Patient Field for Analysis Request '{}' could not "
                "be updated.".format(ar_obj.getId()))
            all_ok = False

        processed += 1
        # log each 250 objects and transaction.commit each 1000
        if processed % 250 == 0:
            logger.info(
                'Progress: {}/{} AnalysisRequest (Samples) have been updated.'
                .format(processed, total))
        if processed % 1000 == 0:
            transaction.commit()
            logger.info('{0} changes commit.'.format(processed))

    transaction.commit()
    logger.info('{0} items processed.'.format(processed))
    return all_ok


def clientpatientid_from_ar_to_sample(ar_obj):
    """
    ClientPatientID has become a proxy field of Sample in AnalysisRequest
    objects. This function migrates ClientPatientID values from the
    AnalysisRequest to the Sample.

    :param ar_obj: AnalysisRequest ATContentType
    :return: True if everything OK, False otherwise.
    """
    # Getting the value directly from schema
    schema = get_schema(ar_obj)
    value = schema.getField('ClientPatientID').get(ar_obj)
    # Setting it, proxy field will do the rest
    schema.getField('ClientPatientID').set(ar_obj, value)
    return True


def patient_from_ar_to_sample(ar_obj):
    """
    Patient field has become a proxy field of Sample in AnalysisRequest
    objects. This function migrates ClientPatientID values from the
    AnalysisRequest to the Sample.

    :param ar_obj: AnalysisRequest ATContentType
    :return: True if everything OK, False otherwise.
    """
    # Getting the value directly from schema
    schema = get_schema(ar_obj)
    value = schema.getField('Patient').get(ar_obj)
    # Setting it, proxy field will do the rest
    schema.getField('Patient').set(ar_obj, value)
    return True
