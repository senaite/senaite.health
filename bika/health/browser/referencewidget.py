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
        adapters = list(getAdapters(params, IReferenceWidgetAdapter))
        if not adapters:
            # No health-specific adapters found, fallback to core's defaults
            return super(ajaxReferenceWidgetSearch, self).search()

        # Do not consider other adapters when an "exclusive" adapter is found
        exclusive = filter(lambda ad:
                           IExclusiveReferenceWidgetAdapter.providedBy(ad[1]),
                           adapters)

        if exclusive:
            if len(exclusive) > 1:
                logger.error("Multiple exclusive adapters found!")
                return []
            adapters = [exclusive[0]]

        brains = []
        for name, adapter in adapters:
            brains.extend(adapter())

        return brains
