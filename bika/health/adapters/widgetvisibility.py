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

from bika.lims.adapters.widgetvisibility import SenaiteATWidgetVisibility


class PatientFieldsVisibility(SenaiteATWidgetVisibility):
    """
    Handles "Batch", "Patient" and "ClientPatientID" fields visibility.
    They are not editable, regardles of the current state of the Sample, except
    when displayed in AR Add view. The reason is that all these fields, together
    with Client field, are strongly related.
    """
    def __init__(self, context):
        super(PatientFieldsVisibility, self).__init__(
            context=context, sort=10,
            field_names=["Batch", "Patient", "ClientPatientID", ])

    def isVisible(self, field, mode="view", default="visible"):
        if mode == "edit":
            return "invisible"
        return default
