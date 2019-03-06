# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.health import bikaMessageFactory as _
from bika.health.utils import get_field_value
from bika.lims import api
from bika.lims.api import security
from bika.lims.permissions import AddBatch
from bika.lims.utils import get_link
from senaite.core.listing import utils
from senaite.core.listing.interfaces import IListingView, IListingViewAdapter
from zope.component import adapts
from zope.interface import implements


class BatchListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    # Order of priority of this subscriber adapter over others
    priority_order = 1

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context
        self.title = self.context.translate(_("Cases"))

    def before_render(self):
        # Additional columns
        self.add_columns()

        # Apply client filter, if necessary
        client = api.get_current_client()
        if client:
            query = dict(getClientUID=api.get_uid(client))
            self.listing.contentFilter.update(query)
            for rv in self.listing.review_states:
                if "contentFilter" not in rv:
                    rv["contentFilter"] = {}
                rv["contentFilter"].update(query)

        # Render the Add button
        self.listing.context_actions = {}
        batches = api.get_portal().batches
        if security.check_permission(AddBatch, batches):
            url = api.get_url(batches)
            self.listing.context_actions = {
                _("Add"): {
                    "url": "{}/createObject?type_name=Batch".format(url),
                    "icon": "++resource++bika.lims.images/add.png"}
            }

    def folder_item(self, obj, item, index):
        batch = api.get_object(obj)
        # Doctor
        doctor = get_field_value(batch, "Doctor", None)
        item["Doctor"] = doctor and doctor.Title() or ""
        item["replace"]["Doctor"] = doctor and get_link(api.get_url(doctor),
                                                        doctor.Title())
        # Onset Date
        onset = get_field_value(batch, "OnsetDate", None)
        item["OnsetDate"] = onset and self.listing.ulocalized_time(onset) or ""

        # Patient
        item["Patient"] = ""
        item["getPatientID"] = ""
        item["getClientPatientID"] = ""
        patient = get_field_value(batch, "Patient", None)
        if patient:
            url = api.get_url(patient)
            item["Patient"] = patient.Title()
            item["replace"]["Patient"] = get_link(url, patient.Title())

            item["getPatientID"] = patient.id
            item["replace"]["getPatientID"] = get_link(url, patient.id)

            pid = patient.getClientPatientID()
            pid_link = pid and get_link(url, pid) or ""
            item["getClientPatientID"] = pid or ""
            item["replace"]["getClientPatientID"] = pid_link

        return item

    def add_columns(self):
        """Adds health-specific columns in the listing
        """
        health_columns = {
            "getPatientID": {
                "title": _("Patient ID"),
                "toggle": True,
                "after": "ClientBatchID",
            },
            "getClientPatientID": {
                "title": _("Client PID"),
                "toggle": True,
                "after": "getPatientID",
            },
            "Patient": {
                "title": _("Patient"),
                "toggle": True,
                "index": "getPatientTitle",
                "after": "getClientPatientID",
            },
            "Doctor": {
                "title": _("Doctor"),
                "index": "getDoctorTitle",
                "after": "Patient",
            },
            "OnsetDate": {
                "title": _("Onset Date"),
                "after": "Patient"
            }
        }

        # Add the columns
        self.listing.columns.update(health_columns)
        rv_keys = map(lambda r: r["id"], self.listing.review_states)
        for column_id, column_values in health_columns.items():
            utils.add_column(listing=self.listing,
                             column_id=column_id,
                             column_values=column_values,
                             after=column_values["after"],
                             review_states=rv_keys)
