# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims import logger
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.interfaces import IAnalysisRequest
from plone.indexer import indexer
from bika.lims.interfaces import IBikaCatalog
from bika.lims.interfaces import IBikaCatalogAnalysisRequestListing


# Defining the indexes for this extension. Since this is an extension, no
# getter is created so we need to create indexes in that way.
# TODO-catalog: delete this index
@indexer(IAnalysisRequest, IBikaCatalog)
def getPatientUID(instance):
    field = instance.getField('Patient', '')
    item = field.get(instance) if field else None
    value = item and item.UID() or ''
    return value


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getPatientUID(instance):
    field = instance.getField('Patient', '')
    item = field.get(instance) if field else None
    value = item and item.UID() or ''
    return value


# We use this index to sort columns and filter lists
@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getPatientTitle(instance):
    field = instance.getField('Patient', '')
    item = field.get(instance) if field else None
    value = item and item.Title() or ''
    return value


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getPatientID(instance):
    field = instance.getField('Patient', '')
    item = field.get(instance) if field else None
    value = item and item.getId() or ''
    return value


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getPatientURL(instance):
    field = instance.getField('Patient', '')
    item = field.get(instance) if field else None
    value = item and api.get_url(item) or ''
    return value


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getClientPatientID(instance):
    field = instance.getField('Patient', '')
    item = field.get(instance) if field else None
    value = item and item.getClientPatientID() or ''
    return value


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getDoctorUID(instance):
    field = instance.getField('Doctor', '')
    item = field.get(instance) if field else None
    value = item and item.UID() or ''
    return value


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getDoctorTitle(instance):
    field = instance.getField('Doctor', '')
    item = field.get(instance) if field else None
    value = item and item.Title() or ''
    return value


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getDoctorURL(instance):
    field = instance.getField('Doctor', '')
    item = field.get(instance) if field else None
    value = item and api.get_url(item) or ''
    return value


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
