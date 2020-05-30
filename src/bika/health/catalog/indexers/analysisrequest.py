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
    return get_attr_from_field(instance, 'Patient', 'UID', '')


# We use this index to sort columns and filter lists
@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getPatientTitle(instance):
    return get_attr_from_field(instance, 'Patient', 'Title', '')



@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getPatientID(instance):
    return get_attr_from_field(instance, 'Patient', 'getId', '')


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getPatientURL(instance):
    item = get_obj_from_field(instance, 'Patient', None)
    return item and item.absolute_url_path() or ''


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getClientPatientID(instance):
    return get_attr_from_field(instance, 'Patient', 'ClientPatientID', '')


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getDoctorUID(instance):
    return get_attr_from_field(instance, 'Doctor', 'UID', '')


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getDoctorTitle(instance):
    return get_attr_from_field(instance, 'Doctor', 'Title', '')


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def getDoctorURL(instance):
    item = get_obj_from_field(instance, 'Doctor', None)
    return item and item.absolute_url_path() or ''

