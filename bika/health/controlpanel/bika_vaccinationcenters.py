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

from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

from bika.health import bikaMessageFactory as _
from bika.health.config import PROJECTNAME
from bika.health.interfaces import IVaccinationCenters
from bika.health.permissions import AddVaccinationCenter
from bika.lims import api
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.catalog.bikasetup_catalog import SETUP_CATALOG
from bika.lims.utils import get_link


# TODO: Separate content and view into own modules!


class VaccinationCentersView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(VaccinationCentersView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG
        self.contentFilter = dict(
            portal_type="VaccinationCenter",
            sort_on="sortable_title"
        )

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=VaccinationCenter",
                "permission": AddVaccinationCenter,
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.title = self.context.translate(_("Vaccination Centers"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.health.images/vaccinationcenter_big.png"
        )

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.columns = collections.OrderedDict((
            ("Name", {
                "title": _("Name"),
                "index": "sortable_title"
            }),
            ("Email", {
                "title": _("Email"),
                "toggle": True
            }),
            ("Phone", {
                "title": _("Phone"),
                "toggle": True
            }),
            ("Fax", {
                "title": _("Fax"),
                "toggle": True
            }),
        ))

        self.review_states = [
            {
                "id":"default",
                "title": _("Active"),
                "contentFilter": {"is_active": True},
                "transitions": [{"id": "deactivate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id":"inactive",
                "title": _("Dormant"),
                "contentFilter": {"is_active": False},
                "transitions": [{"id": "activate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id":"all",
                "title": _("All"),
                "contentFilter":{},
                "columns": self.columns.keys(),
            },
        ]

    def before_render(self):
        """Before template render hook
        """
        super(VaccinationCentersView, self).before_render()
        # Don"t allow any context actions
        self.request.set("disable_border", 1)

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.
        The use of this service prevents the extra-loops in child objects.
        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        obj = api.get_object(obj)
        name = obj.getName()
        url = api.get_url(obj)

        item["Email"] = obj.getEmailAddress()
        item["Phone"] = obj.getPhone()
        item["Fax"] = obj.getFax()
        item["replace"]["Name"] = get_link(url, value=name)

        return item


schema = ATFolderSchema.copy()


class VaccinationCenters(ATFolder):
    implements(IVaccinationCenters)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(VaccinationCenters, PROJECTNAME)
