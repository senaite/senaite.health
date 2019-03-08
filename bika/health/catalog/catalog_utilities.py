# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.health.catalog.analysisrequest_catalog import\
    analysisrequest_catalog_definition
from bika.health.catalog.patient_catalog import patient_catalog_definition


def getCatalogDefinitions():
    """
    Returns a dictionary with catalog definitions
    """
    return patient_catalog_definition


# TODO Remove getCatalogExtensions
def getCatalogExtensions():
    """
    Returns a dictionary with catalog extensions
    """
    return analysisrequest_catalog_definition
