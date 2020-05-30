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

from ZODB.POSException import POSKeyError
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import get_link
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class PatientMultifileView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(PatientMultifileView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "Multifile",
            "path": {
                "query": api.get_path(context),
                "depth": 1  # searching just inside the specified folder
            },
            "sort_on": "created",
            "sort_order": "descending",
        }

        self.form_id = "patientfiles"
        self.title = self.context.translate(_("Patient Files"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/instrumentcertification_big.png"
        )
        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=Multifile",
                "icon": "++resource++bika.lims.images/add.png"
            }
        }

        self.allow_edit = False
        self.show_select_column = False
        self.show_workflow_action_buttons = True
        self.pagesize = 30

        self.columns = {
            "DocumentID": {"title": _("Document ID"),
                           "index": "sortable_title"},
            "DocumentVersion": {"title": _("Document Version"),
                                "index": "sortable_title"},
            "DocumentLocation": {"title": _("Document Location"),
                                 "index": "sortable_title"},
            "DocumentType": {"title": _("Document Type"),
                             "index": "sortable_title"},
            "FileDownload": {"title": _("File")}
        }

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "columns": [
                    "DocumentID",
                    "DocumentVersion",
                    "DocumentLocation",
                    "DocumentType",
                    "FileDownload"
                ]
            },
        ]

    def get_file(self, obj):
        """Return the file of the given object
        """
        try:
            return obj.getFile()
        except POSKeyError:  # POSKeyError: "No blob file"
            # XXX When does this happen?
            return None

    def folderitem(self, obj, item, index):
        """Augment folder listing item with additional data
        """
        obj = api.get_object(obj)
        url = item.get("url")
        title = item.get("DocumentID")

        item["replace"]["DocumentID"] = get_link(url, title)

        item["FileDownload"] = ""
        item["replace"]["FileDownload"] = ""
        file = self.get_file(obj)
        if file and file.get_size() > 0:
            filename = file.filename
            download_url = "{}/at_download/File".format(url)
            anchor = get_link(download_url, filename)
            item["FileDownload"] = filename
            item["replace"]["FileDownload"] = anchor

        item["DocumentVersion"] = obj.getDocumentVersion()
        item["DocumentLocation"] = obj.getDocumentLocation()
        item["DocumentType"] = obj.getDocumentType()
        return item
