# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from plone.indexer import indexer

from bika.health.utils import get_obj_from_field, get_attr_from_field
from bika.lims import api
from bika.lims import logger
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IBikaCatalogAnalysisRequestListing


# Defining the indexes for this extension. Since this is an extension, no
# getter is created so we need to create indexes in that way.
@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getPatientUID(instance):
    return get_attr_from_field(instance, 'Patient', 'UID')


# We use this index to sort columns and filter lists
@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getPatientTitle(instance):
    return get_attr_from_field(instance, 'Patient', 'Title')



@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getPatientID(instance):
    return get_attr_from_field(instance, 'Patient', 'Id')


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getPatientURL(instance):
    item = get_obj_from_field(instance, 'Patient')
    return api.get_url(item) or ''


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getClientPatientID(instance):
    return get_attr_from_field(instance, 'Patient', 'ClientPatientID')


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getDoctorUID(instance):
    return get_attr_from_field(instance, 'Doctor', 'UID')


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getDoctorTitle(instance):
    return get_attr_from_field(instance, 'Doctor', 'Title')


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getDoctorURL(instance):
    item = get_obj_from_field(instance, 'Doctor')
    return api.get_url(item) or ''


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def listing_searchable_text(instance):
    """ Retrieves all the values of metadata columns in the catalog for
    wildcard searches
    :return: all metadata values joined in a string
    """
    entries = []
    catalog = api.get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    columns = catalog.schema()
    failed_columns = []
    for column in columns:
        try:
            value = api.safe_getattr(instance, column)
        except:
            failed_columns.append(column)
            continue
        if not value:
            continue
        parsed = api.to_searchable_text_metadata(value)
        entries.append(parsed)

    # Getters of senaite.health extension fields are not created. That's why
    # we are adding them manually
    for failed_column in failed_columns:
        getter = globals().get(failed_column, None)
        if not getter:
            logger.error("{} has no attribute called '{}' ".format(
                            repr(instance), failed_column))
            continue
        value = getter(instance)()
        if not value:
            continue
        parsed = api.to_searchable_text_metadata(value)
        entries.append(parsed)

    # Concatenate all strings to one text blob
    return " ".join(entries)
