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

import collections

from senaite.core.listing import utils
from senaite.core.listing.interfaces import IListingView
from senaite.core.listing.interfaces import IListingViewAdapter
from zope.component import adapts
from zope.interface import implements

from bika.health import bikaMessageFactory as _
from bika.health.utils import get_age_ymd
from bika.health.utils import get_client_aware_html_image
from bika.health.utils import get_client_from_chain
from bika.health.utils import get_field_value
from bika.health.utils import is_from_external_client
from bika.health.utils import is_logged_user_from_external_client
from bika.lims import AddBatch
from bika.lims import api
from bika.lims.utils import get_image
from bika.lims.utils import get_link


class BatchListingViewAdapter(object):
    """Adapter for generic Batch listings
    """
    adapts(IListingView)
    implements(IListingViewAdapter)

    # Order of priority of this subscriber adapter over others
    priority_order = 1

    _is_in_client = None
    _is_client_user = None
    _is_external_user = None

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context
        self.title = self.context.translate(_("Cases"))

    @property
    def is_external_user(self):
        """Returns whether the current user belongs to an external client
        """
        if self._is_external_user is None:
            self._is_external_user = is_logged_user_from_external_client()
        return self._is_external_user

    @property
    def is_client_user(self):
        """Returns whether the current user belongs to an internal client
        """
        if self._is_client_user is None:
            self._is_client_user = api.get_current_client() and True or False
        return self._is_client_user

    @property
    def is_in_client(self):
        """Returns whether the current context is from inside a client
        """
        if self._is_in_client is None:
            client = get_client_from_chain(self.context)
            self._is_in_client = client and True or False
        return self._is_in_client

    def before_render(self):
        # Rename columns BatchID and ClientBatchID
        self.listing.columns["BatchID"]["title"] = _("Case ID")
        self.listing.columns["ClientBatchID"]["title"] = _("Client Case ID")

        # Change the contentFilter and transitions from review_states
        self.update_review_states()

        # Additional review_satuses
        self.add_review_states()

        # Additional columns
        self.add_columns()

        # Remove unnecessary columns
        column_ids = ["Title", "BatchDate", "Description", ]
        if self.is_client_user or self.is_in_client:
            # Hide client-specific columns
            column_ids.extend(["Client", "ClientID"])

        self.hide_columns(column_ids)

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
        item["PatientAgeOnsetDate"] = ""
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

            dob = patient.getBirthDate()
            if onset and dob:
                try:
                    age_ymd = get_age_ymd(patient.getBirthDate(), onset)
                    item["replace"]["PatientAgeOnsetDate"] = age_ymd
                except:
                    # Wrong date??
                    msg = _("Date of Birth or Case Onset Date are wrong")
                    img = get_image("exclamation.png", title=msg)
                    item["replace"]["PatientAgeOnsetDate"] = img

        # Display the internal/external icons, but only if the logged-in user
        # does not belong to an external client
        if not self.is_external_user:
            item["before"]["BatchID"] = get_client_aware_html_image(obj)

        return item

    def update_review_states(self):
        """Updates the contentFilter and transitions from review states
        """
        for rv in self.listing.review_states:
            if rv["id"] == "default":
                rv["contentFilter"].update({"review_state": ["open", "shared"]})

            # TODO Remove after core's PR#1577 gets accepted
            # https://github.com/senaite/senaite.core/pull/1577
            rv["transitions"] = []

    def add_review_states(self):
        if self.is_external_user:
            # If the logged in user is external, there is no need to display
            # shared/private filters, it might cause confusion
            return

        # Do not display the filters unless current context is not inside an
        # external client
        if not is_from_external_client(self.context):
            self.listing.review_states.insert(1, {
                "id": "shared",
                "title": _("Open (shared)"),
                "contentFilter": {"review_state": "shared"},
                "transitions": [],
                "columns": self.listing.columns.keys(),
            })
            self.listing.review_states.insert(2, {
                "id": "private",
                "title": _("Open (private)"),
                "contentFilter": {"review_state": "private"},
                "transitions": [],
                "columns": self.listing.columns.keys(),
            })

    def hide_columns(self, column_ids):
        """Hides columns from the listing
        """
        for column_id in column_ids:
            self.listing.columns[column_id]["toggle"] = False

    def add_columns(self):
        """Adds health-specific columns in the listing
        """
        health_columns = collections.OrderedDict((
            ("getPatientID", {
                "title": _("Patient ID"),
                "toggle": True,
                "after": "ClientBatchID", }),
            ("getClientPatientID", {
                "title": _("Client PID"),
                "toggle": True,
                "after": "getPatientID", }),
            ("Patient", {
                "title": _("Patient"),
                "toggle": True,
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
            ("PatientAgeOnsetDate", {
                "title": _("Patient Age"),
                "sortable": False,
                "after": "OnsetDate", }),
        ))

        # Add the columns
        rv_keys = map(lambda r: r["id"], self.listing.review_states)
        for column_id, column_values in health_columns.items():
            utils.add_column(listing=self.listing,
                             column_id=column_id,
                             column_values=column_values,
                             after=column_values["after"],
                             review_states=rv_keys)


class PatientBatchListingViewAdapter(BatchListingViewAdapter):
    """Adapter for Patient's Batch listings
    """

    def before_render(self):
        """Called before the listing renders
        """
        super(PatientBatchListingViewAdapter, self).before_render()

        # Remove unnecessary columns
        hide = ["getPatientID", "getClientPatientID", "Patient", ]
        self.hide_columns(hide)

        # Filter by patient
        query = dict(getPatientUID=api.get_uid(self.context))
        self.listing.contentFilter.update(query)
        for rv in self.listing.review_states:
            if "contentFilter" not in rv:
                rv["contentFilter"] = {}
            rv["contentFilter"].update(query)

        url = api.get_url(self.context)
        self.listing.context_actions = {
            _("Add"): {
                "url": "{}/createObject?type_name=Batch".format(url),
                "permission": AddBatch,
                "icon": "++resource++bika.lims.images/add.png"
            }
        }


class DoctorBatchListingViewAdapter(BatchListingViewAdapter):
    """Adapter for Doctor's Batch listings
    """

    def before_render(self):
        """Called before the listing renders
        """
        super(DoctorBatchListingViewAdapter, self).before_render()

        # Remove unnecessary columns
        hide = ["Doctor", ]
        self.hide_columns(hide)

        # Filter by doctor
        query = dict(getDoctorUID=api.get_uid(self.context))
        self.listing.contentFilter.update(query)
        for rv in self.listing.review_states:
            if "contentFilter" not in rv:
                rv["contentFilter"] = {}
            rv["contentFilter"].update(query)

        url = api.get_url(self.context)
        self.listing.context_actions = {
            _("Add"): {
                "url": "{}/createObject?type_name=Batch".format(url),
                "permission": AddBatch,
                "icon": "++resource++bika.lims.images/add.png"
            }
        }
