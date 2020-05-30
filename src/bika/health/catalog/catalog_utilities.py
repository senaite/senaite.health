# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH.
#
# SENAITE.HEALTH is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

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
