# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.
from bika.health.catalog.patient_catalog import CATALOG_PATIENT_LISTING
from bika.health.interfaces import IPatient
from bika.lims import api
from bika.lims import logger
from plone.indexer import indexer

@indexer(IPatient)
def listing_searchable_text(instance):
    """ Retrieves all the values of metadata columns in the catalog for
    wildcard searches
    :return: all metadata values joined in a string
    """
    entries = []
    catalog = api.get_tool(CATALOG_PATIENT_LISTING)
    columns = catalog.schema()
    brains = catalog({"UID": api.get_uid(instance)})
    brain = brains[0] if brains else None
    for column in columns:
        brain_value = api.safe_getattr(brain, column, None)
        instance_value = api.safe_getattr(instance, column, None)
        parsed = api.to_searchable_text_metadata(brain_value or instance_value)
        entries.append(parsed)

    # Concatenate all strings to one text blob
    return " ".join(entries)
