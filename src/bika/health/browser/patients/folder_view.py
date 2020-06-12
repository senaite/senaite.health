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

from plone.memoize import view

from bika.health import bikaMessageFactory as _
from bika.health.catalog import CATALOG_PATIENTS
from bika.health.interfaces import IPatients
from bika.health.permissions import AddPatient
from bika.health.utils import get_age_ymd
from bika.health.utils import get_client_aware_html_image
from bika.health.utils import get_client_from_chain
from bika.health.utils import get_resource_url
from bika.health.utils import is_from_external_client
from bika.lims import api
from bika.lims.api.security import check_permission
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import get_image
from bika.lims.utils import get_link


class PatientsView(BikaListingView):
    """Listing View for all Patients in the System
    """

    def __init__(self, context, request):
        super(PatientsView, self).__init__(context, request)
        self.title = self.context.translate(_("Patients"))
        self.icon = get_resource_url("patient_big.png")
        self.form_id = "list_health_patients"
        self.show_select_row = False
        self.show_select_column = True
        self.show_select_all_checkboxes = False

        self.sort_on = "created"
        self.catalog = CATALOG_PATIENTS
        self.contentFilter = {'portal_type': 'Patient',
                              'sort_on': 'created',
                              'sort_order': 'descending'}

        client = self.get_client()
        if client:
            # Display the Patients the belong to this Client only
            self.contentFilter["path"] = {
                "query": api.get_path(client), "depth": 1
            }

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Patient"),
                "index": "getFullname",}),

            ('getPatientID', {
                'title': _('Patient ID'),
                'index': 'getPatientID'}),

            ('getClientPatientID', {
                'title': _('Client PID'),
                'sortable': False}),

            ('getGender', {
                'title': _('Gender'),
                'toggle': True,
                'sortable': False}),

            ('age', {
                'title': _('Age'),
                'toggle': True,
                'sortable': False}),

            ('getBirthDate', {
                'title': _('BirthDate'),
                'toggle': True,
                'sortable': False}),

            ('getPrimaryReferrerTitle', {
                'title': _('Primary Referrer'),
                'replace_url': 'getPrimaryReferrerURL',
                'toggle': True,
                'sortable': False}),

            ('getPatientIdentifiersStr', {
                'title': _('Additional IDs'),
                'attr': 'getPatientIdentifiersStr',
                'toggle': False,
                'sortable': False}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"is_active": True},
                "transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {'is_active': False},
                "transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

        if not self.is_external_user():
            external = client and is_from_external_client(client)
            if not external:
                # Neither the client nor the current user are external
                # Display share/private filters
                self.review_states.insert(1, {
                    "id": "shared",
                    "title": _("Active (shared)"),
                    "contentFilter": {"review_state": "shared"},
                    "transitions": [],
                    "columns": self.columns.keys(),
                })
                self.review_states.insert(2, {
                    "id": "private",
                    "title": _("Active (private)"),
                    "contentFilter": {"review_state": "active"},
                    "transitions": [],
                    "columns": self.columns.keys(),
                })

    @view.memoize
    def get_client(self):
        """Returns the client this context is from, if any
        """
        return get_client_from_chain(self.context)

    @view.memoize
    def get_user_client(self):
        """Returns the client from current user, if any
        """
        return api.get_current_client()

    @view.memoize
    def is_external_user(self):
        """Returns whether the current user belongs to an external client
        """
        client = self.get_user_client()
        if not client:
            return False
        return is_from_external_client(client)

    def update(self):
        """Before template render hook
        """
        super(PatientsView, self).update()

        if IPatients.providedBy(self.context):
            # Top-level patients listing
            self.request.set("disable_border", 1)

        elif "disable_border" in self.request:
            del(self.request["disable_border"])

        # By default, only users with AddPatient permissions for the current
        # context can add patients.
        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=Patient",
                "permission": AddPatient,
                "icon": "++resource++bika.lims.images/add.png"
            }
        }

        # If current user is a client contact, then modify the url for Add
        # action so the Patient gets created, inside the Client object to which
        # the current user belongs. The reason is that the permission
        # "AddPatient" for client contacts in base folders is not granted
        client = self.get_user_client()
        if client and check_permission(AddPatient, client):
            add_url = self.context_actions[_("Add")]["url"]
            add_url = "{}/{}".format(api.get_url(client), add_url)
            self.context_actions[_("Add")]["url"] = add_url
            del(self.context_actions[_("Add")]["permission"])

        if self.get_client():
            # The current context belongs to a Client, remove the title column
            self.remove_column('getPrimaryReferrerTitle')

    def folderitem(self, obj, item, index):
        # Date of Birth
        dob = obj.getBirthDate
        item['getBirthDate'] = dob and self.ulocalized_time(dob) or ""
        try:
            item["age"] = dob and get_age_ymd(dob) or ""
        except:
            # Wrong date??
            msg = _("Date of Birth might be wrong")
            img = get_image("exclamation.png", title=msg)
            item["replace"]["age"] = img

        # make the columns patient title, patient ID and client patient ID
        # redirect to the Analysis Requests of the patient
        ars_url = "{}/{}".format(api.get_url(obj), "analysisrequests")
        for column in ['Title', 'getPatientID', 'getClientPatientID']:
            value = getattr(obj, column, None)
            if value:
                item["replace"][column] = get_link(ars_url, value)

        # Display the internal/external icons, but only if the logged-in user
        # does not belong to an external client
        if not self.is_external_user():
            # Renders an icon (shared/private/warn) next to the title of the
            # item based on the client
            item["before"]["Title"] = get_client_aware_html_image(obj)

        return item
