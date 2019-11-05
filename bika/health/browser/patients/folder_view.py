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
from bika.health.interfaces import IPatients
from bika.health.utils import get_resource_url
from bika.health.catalog import CATALOG_PATIENTS
from bika.health.permissions import AddPatient
from bika.lims import api
from bika.lims.api import security
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IClient
from bika.lims.utils import get_link
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from bika.lims.api.security import check_permission


class PatientsView(BikaListingView):
    """Listing View for all Patients in the System
    """
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(PatientsView, self).__init__(context, request)
        self.title = self.context.translate(_("Patients"))
        self.icon = get_resource_url("patient_big.png")
        self.form_id = "list_health_patients"
        self.show_select_row = False
        self.show_select_column = True
        self.show_select_all_checkboxes = False
        request.set("disable_border", 1)

        self.sort_on = "created"
        self.catalog = CATALOG_PATIENTS
        self.contentFilter = {'portal_type': 'Patient',
                              'sort_on': 'created',
                              'sort_order': 'descending'}

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Patient"),
                "index": "getFullname",
                "replace_url": "absolute_url"}),

            ('getPatientID', {
                'title': _('Patient ID'),
                'index': 'getPatientID',
                'replace_url': 'getURL'}),

            ('getClientPatientID', {
                'title': _('Client PID'),
                'replace_url': 'getURL',
                'sortable': False}),

            ('getGender', {
                'title': _('Gender'),
                'toggle': True,
                'sortable': False}),

            ('getAgeSplittedStr', {
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

    def before_render(self):
        """Before template render hook
        """
        super(PatientsView, self).before_render()

        if IPatients.providedBy(self.context):
            self.request.set("disable_border", 1)

        # By default, only users with AddPatient permissions for the current
        # context can add patients.
        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=Patient",
                "permission": AddPatient,
                "icon": "++resource++bika.lims.images/add.png"
            }
        }

        # If current user is a client contact and current context is not a
        # Client, then modify the url for Add action so the Patient gets created
        # inside the Client object to which the current user belongs. The
        # reason is that Client contacts do not have privileges to create
        # Patients inside portal/patients
        if not IClient.providedBy(self.context):
            # Get the client the current user belongs to
            client = api.get_current_client()
            if client and check_permission(AddPatient, client):
                add_url = self.context_actions[_("Add")]["url"]
                add_url = "{}/{}".format(api.get_url(client), add_url)
                self.context_actions[_("Add")]["url"] = add_url
                del(self.context_actions[_("Add")]["permission"])

        else:
            # The current context is a Client, remove the title column
            self.remove_column('getPrimaryReferrerTitle')

    def folderitems(self, full_objects=False, classic=False):
        # Force the folderitems to work with brains instead of objects
        return BikaListingView.folderitems(self, classic=classic)

    def folderitem(self, obj, item, index):
        item['getBirthDate'] = self.ulocalized_time(obj.getBirthDate)
        # make the columns patient title, patient ID and client patient ID
        # redirect to the Analysis Requests of the patient
        ars_url = "{}/{}".format(api.get_url(obj), "analysisrequests")
        for column in ['Title', 'getPatientID', 'getClientPatientID']:
            value = getattr(obj, column, None)
            if value:
                item["replace"][column] = get_link(ars_url, value)
        return item
