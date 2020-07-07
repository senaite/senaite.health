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

from zope.component import getAdapters

from bika.health import logger
from bika.health.adapters.referencewidget import IReferenceWidgetAdapter
from bika.health.adapters.referencewidget import IExclusiveReferenceWidgetAdapter
from bika.lims.browser.widgets.referencewidget import \
    ajaxReferenceWidgetSearch as base


class ajaxReferenceWidgetSearch(base):
    """
    End-point for reference widget searches in senaite.health. Does the same
    as the base class, except that gives priority to reference widget vocabulary
    adapters for IReferenceWidgetAdapter (from senaite.health)
    """

    def search(self):
        """Returns the list of brains that match with the request criteria
        """
        params = (self.context, self.request)
        adapters = list(getAdapters(params, IReferenceWidgetAdapter)) or []

        # Convert adapters to a list (don't need the name)
        adapters = map(lambda ad: ad[1], adapters)

        # Filter supported adapters
        adapters = filter(lambda ad: ad.is_supported(), adapters)

        if not adapters:
            # Fallback to core's defaults
            return super(ajaxReferenceWidgetSearch, self).search()

        # Do not consider other adapters when an "exclusive" adapter is found
        exclusive = filter(lambda adapter:
                           IExclusiveReferenceWidgetAdapter.providedBy(adapter),
                           adapters)

        if exclusive and len(exclusive) > 1:
            logger.error("Multiple exclusive adapters found!")
            # We do not fallback to core's default. We return empty to prevent
            # inconsistencies
            return []

        elif exclusive:
            # Discard other adapters
            adapters = [exclusive[0]]

        brains = []
        for adapter in adapters:
            brains.extend(adapter())

        return brains
