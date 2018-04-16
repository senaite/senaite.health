# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims import logger
from bika.lims.interfaces import IAnalysisRequest
from plone.indexer import indexer
from bika.lims.interfaces import IBikaCatalogAnalysisRequestListing


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def listing_searchable_text(instance):
    """ Indexes values of desired fields for searches in listing view. All the
    field names added to 'plain_text_fields' will be available to search by
    wildcards.
    Please choose the searchable fields carefully and add only fields that
    can be useful to search by. For example, there is no need to add 'SampleId'
    since 'getId' of AR already contains that value. Nor 'ClientTitle' because
    AR's are/can be filtered by client in Clients' 'AR Listing View'
    :return: values of the fields defined as a string
    """
    entries = []
    plain_text_fields = ('getId', 'getContactFullName', 'getSampleTypeTitle',
                         'getSamplePointTitle')

    # Concatenate plain text fields as they are
    for field_name in plain_text_fields:
        try:
            value = api.safe_getattr(instance, field_name)
        except:
            logger.error("{} has no attribute called '{}' ".format(
                            repr(instance), field_name))
            continue
        entries.append(value)

    # Getter of senaite.health extension fields are not created. That's why
    # we are adding them manually
    patient_field = instance.getField('Patient', '')
    patient = patient_field.get(instance) if patient_field else None
    if patient:
        entries.extend((patient.getId(), patient.Title()))

    doctor_field = instance.getField('Doctor', '')
    doctor = doctor_field.get(instance) if doctor_field else None
    if doctor:
        entries.extend((doctor.getId(), doctor.Title()))

    # Concatenate all strings to one text blob
    return " ".join(entries)
