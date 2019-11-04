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

from bika.health.interfaces import IPatient
from bika.lims.interfaces import IClient


def getClient(self):
    """Returns the Client from the Batch passed-in, if any
    """
    # The schema's field Client is only used to allow the user to assign
    # the batch to a client in edit form. The entered value is used in
    # ObjectModifiedEventHandler to move the batch to the Client's folder,
    # so the value stored in the Schema's is not used anymore
    # See https://github.com/senaite/senaite.core/pull/1450
    parent = self.aq_parent
    if IClient.providedBy(parent):
        return parent

    elif IPatient.providedBy(parent):
        return parent.getClient()

    return None
