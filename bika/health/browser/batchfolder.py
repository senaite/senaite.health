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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections

from bika.health import bikaMessageFactory as _
from bika.health.utils import get_field_value
from bika.lims import api
from bika.lims.interfaces import IClient
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
        # Remove unnecessary columns
        self.hide_columns()


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

    def is_client_context(self):
        """Returns whether the batch listing is displayed in IClient context
        or if the current user is a client contact
        """
        return api.get_current_client() or IClient.providedBy(self.context)

    def hide_columns(self):
        # Columns to hide
        hide = ["Title", "BatchDate", "Description",]
        if api.get_current_client():
            # Hide client-specific columns
            hide.extend(["Client", "ClientID"])

        # Remove the columns from all review_states
        for rv in self.listing.review_states:
            rv_columns = rv.get("columns", self.listing.columns.keys())
            rv_columns = filter(lambda col: col not in hide, rv_columns)
            rv["columns"] = rv_columns

    def add_columns(self):
        """Adds health-specific columns in the listing
        """
        is_client_context = self.is_client_context()
        health_columns = collections.OrderedDict((
            ("getPatientID", {
                "title": _("Patient ID"),
                "toggle": is_client_context,
                "after": "ClientBatchID", }),
            ("getClientPatientID", {
                "title": _("Client PID"),
                "toggle": is_client_context,
                "after": "getPatientID", }),
            ("Patient", {
                "title": _("Patient"),
                "toggle": is_client_context,
                "index": "getPatientTitle",
                "after": "getClientPatientID", }),
            ("Doctor", {
                "title": _("Doctor"),
                "toggle": True,
                "index": "getDoctorTitle",
                "after": "Patient", }),
            ("OnsetDate", {
                "title": _("Onset Date"),
                "toggle": True,
                "after": "Patient", }),
        ))

        # Add the columns
        rv_keys = map(lambda r: r["id"], self.listing.review_states)
        for column_id, column_values in health_columns.items():
            utils.add_column(listing=self.listing,
                             column_id=column_id,
                             column_values=column_values,
                             after=column_values["after"],
                             review_states=rv_keys)
