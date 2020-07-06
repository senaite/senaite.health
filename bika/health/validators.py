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

from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import to_utf8
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator
from datetime import datetime
from bika.lims import api
from bika.health.catalog.patient_catalog import CATALOG_PATIENTS


class Date_Format_Validator:

    """ Verifies whether the format is the correct or not """

    implements(IValidator)
    name = "isDateFormat"

    def __call__(self, value, *args, **kwargs):
        field = kwargs.get('field', None)
        required = hasattr(field, "required") and field.required or False
        if not value and not required:
            return True

        if api.is_date(value):
            return True

        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            instance = kwargs['instance']
            title = kwargs['field'].widget.label
            trans = getToolByName(instance, 'translation_service').translate
            msg = _(
                "Incorrect data format in '${title}', should be YYYY-MM-DD",
                mapping={'title': safe_unicode(value)}
            )
            return to_utf8(trans(msg))
        return True


validation.register(Date_Format_Validator())


class UniqueClientPatientIDValidator:
    """
    Checks if the client patient ID is unique. It does
    so only if the checkbox 'Client Patient ID must be
    unique' is selected . This checkbox can be found in
    Bika Setup under Id server tab
    """

    implements(IValidator)
    name = "unique_client_patient_ID_validator"

    def __call__(self, value, *args, **kwargs):
        # avoid the catalog query if the option is not selected
        setup = api.get_setup()
        if not getattr(setup, "ClientPatientIDUnique", False):
            return True
        query = dict(getClientPatientID=value)
        patients = api.search(query, CATALOG_PATIENTS)
        instance = kwargs.get('instance')
        # If there are no patients with this Client Patient ID
        # then it is valid
        if not patients:
            return True
        # If there is only one patient with this Client Patient ID
        # and it is the patient being edited then it also valid
        if len(patients) == 1 and api.get_uid(patients[0]) == api.get_uid(instance):
            return True
        trans = getToolByName(instance, 'translation_service').translate
        msg = _(
            "Validation failed: '${value}' is not unique",
            mapping={
                'value': safe_unicode(value)
            })
        return to_utf8(trans(msg))


validation.register(UniqueClientPatientIDValidator())
