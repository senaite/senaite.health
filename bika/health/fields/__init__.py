"""Generic field extensions"""

from Products.Archetypes.public import *
from archetypes.schemaextender.field import ExtensionField
from Products.ATExtensions.ateapi import RecordField, RecordsField
from Products.ATExtensions.ateapi import DateTimeField

class ExtBooleanField(ExtensionField, BooleanField):
    "Field extender"

class ExtComputedField(ExtensionField, ComputedField):
    "Field extender"

class ExtDateTimeField(ExtensionField, DateTimeField):
    "Field extender"

class ExtIntegerField(ExtensionField, IntegerField):
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
