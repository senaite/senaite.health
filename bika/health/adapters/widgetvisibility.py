# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
