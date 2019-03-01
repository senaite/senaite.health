# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections

from bika.health import bikaMessageFactory as _
from bika.health.utils import get_resource_url
from bika.health.catalog import CATALOG_PATIENTS
from bika.health.permissions import AddPatient
from bika.lims import api
from bika.lims.api import security
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import get_link
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


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
        self.show_select_column = False
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

    def update(self):
        """Called before the listings renders
        """
        super(PatientsView, self).update()

        # Render the Add button. We need to do this here because patients live
        # inside site.patients folder
        # TODO Security Patients should live inside Client folders!
        patients = api.get_portal().patients
        if security.check_permission(AddPatient, patients):
            self.context_actions = {
                _("Add"): {
                    "url": "createObject?type_name=Patient",
                    "icon": "++resource++bika.lims.images/add.png"}
            }

        # If the current user is a client contact, display those patients that
        # belong to same client or that do not belong to any client
        client = api.get_current_client()
        if client:
            query = dict(client_uid=[api.get_uid(client), "-1"])
            # We add UID "-1" to also include Patients w/o Client assigned
            self.contentFilter.update(query)
            for rv in self.review_states:
                rv["contentFilter"].update(query)

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
