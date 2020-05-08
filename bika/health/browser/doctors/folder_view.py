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

from collections import OrderedDict

from plone.memoize import view

from bika.health import bikaMessageFactory as _
from bika.health.interfaces import IDoctors
from bika.health.permissions import *
from bika.health.utils import get_client_aware_html_image
from bika.health.utils import get_client_from_chain
from bika.health.utils import get_resource_url
from bika.health.utils import is_from_external_client
from bika.lims import api
from bika.lims.api.security import check_permission
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import get_email_link
from bika.lims.utils import get_link


class DoctorsView(BikaListingView):
    """Listing view for Doctors
    """

    def __init__(self, context, request):
        super(DoctorsView, self).__init__(context, request)
        self.title = self.context.translate(_("Doctors"))
        self.icon = get_resource_url("doctor_big.png")
        self.form_id = "list_health_doctors"
        self.show_select_row = False
        self.show_select_column = True
        self.show_select_all_checkboxes = False

        self.sort_on = "getFullname"
        self.contentFilter = {"portal_type": "Doctor",
                              "sort_on": "getFullname",
                              "sort_order": "ascending"}

        client = self.get_client()
        if client:
            # Display the Doctors that belong to this Client only
            self.contentFilter["path"] = {
                "query": api.get_path(client), "depth": 1
            }

        self.columns = OrderedDict((
            ("getFullname", {
                "title": _("Full Name"),
                "index": "getFullname",
                "toggle": True,
                "sortable": True, }),

            ("getDoctorID", {
                "title": _('Doctor ID'),
                "index": "getDoctorID",
                "toggle": True,
                "sortable": True, }),

            ("getPrimaryReferrer", {
                "title": _("Client"),
                "toggle": True,
                "sortable": True, }),

            ("Department", {
                "title": _("Department"),
                "toggle": True,
                "sortable": False, }),

            ("Username", {
                "title": _("User Name"),
                "toggle": False, }),

            ("getEmailAddress", {
                "title": _("Email Address"),
                "toggle": True, }),

            ("getBusinessPhone", {
                "title": _("Business Phone"),
                "toggle": False, }),

            ("getMobilePhone", {
                "title": _("MobilePhone"),
                "toggle": False, }),
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
        super(DoctorsView, self).update()

        if IDoctors.providedBy(self.context):
            # Top-level doctors listing
            self.request.set("disable_border", 1)

        elif "disable_border" in self.request:
            del(self.request["disable_border"])

        # By default, only users with AddDoctor permissions for the current
        # context can add doctors.
        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=Doctor",
                "permission": AddDoctor,
                "icon": "++resource++bika.lims.images/add.png"
            }
        }

        # If current user is a client contact and current context is not a
        # Client, then modify the url for Add action so the Doctor gets created
        # inside the Client object the current user belongs to
        client = self.get_user_client()
        if client and check_permission(AddDoctor, client):
            add_url = self.context_actions[_("Add")]["url"]
            add_url = "{}/{}".format(api.get_url(client), add_url)
            self.context_actions[_("Add")]["url"] = add_url
            del(self.context_actions[_("Add")]["permission"])

        if self.get_client():
            # The current context is a Client, remove the client column
            self.remove_column('getPrimaryReferrer')

    def folderitem(self, obj, item, index):
        """Applies new properties to the item to be rendered
        """
        obj = api.get_object(obj)
        # Replace client name with the link
        item['getPrimaryReferrer'] = ""
        client = obj.getClient()
        if client:
            client_link = get_link(api.get_url(client), api.get_title(client))
            item["replace"]["getPrimaryReferrer"] = client_link

        # Replace doctor's full name with a link
        fullname = obj.getFullname()
        doctor_url = "{}/analysisrequests".format(api.get_url(obj))
        doctor_link = get_link(doctor_url, fullname)
        item["replace"]["getFullname"] = doctor_link
        doctor_link = get_link(doctor_url, obj.getDoctorID())
        item["replace"]["getDoctorID"] = doctor_link

        # Replace doctor's full name with a link
        email = obj.getEmailAddress()
        if email:
            item["replace"]['getEmailAddress'] = get_email_link(email)

        # Display the internal/external icons, but only if the logged-in user
        # does not belong to an external client
        if not self.is_external_user():
            item["before"]["getFullname"] = get_client_aware_html_image(obj)

        return item
