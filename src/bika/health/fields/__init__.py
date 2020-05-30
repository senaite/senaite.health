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

"""Generic field extensions"""

from Products.Archetypes.public import *
from archetypes.schemaextender.field import ExtensionField
from Products.ATExtensions.ateapi import RecordField, RecordsField
from Products.ATExtensions.ateapi import DateTimeField


class field_getter:
    "Used to mimic the Archetypes automatically generated accessor"

    def __init__(self, context, fieldname):
        self.context = context
        self.fieldname = fieldname

    def __call__(self):
        return self.context.Schema()[self.fieldname].getAccessor(self.context)()


class field_setter:
    "Used to mimic the Archetypes automatically generated mutator"

    def __init__(self, context, fieldname):
        self.context = context
        self.fieldname = fieldname

    def __call__(self, value):
        return self.context.Schema()[self.fieldname].getMutator(self.context)(value)


class ExtBooleanField(ExtensionField, BooleanField):
    "Field extender"


class ExtComputedField(ExtensionField, ComputedField):
    "Field extender"


class ExtDateTimeField(ExtensionField, DateTimeField):
    "Field extender"


class ExtIntegerField(ExtensionField, IntegerField):
    "Field extender"

class ExtLinesField(ExtensionField, LinesField):
    "Field extender"

class ExtRecordField(ExtensionField, RecordField):
    "Field extender"


class ExtRecordsField(ExtensionField, RecordsField):
    "Field extender"


class ExtReferenceField(ExtensionField, ReferenceField):
    "Field extender"


class ExtStringField(ExtensionField, StringField):
    "Field extender"


class ExtTextField(ExtensionField, TextField):
    "Field extender"
