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

from plone.indexer import indexer

from bika.health.utils import get_field_value
from bika.lims import api
from bika.lims.interfaces import IBatch


@indexer(IBatch)
def getPatientID(instance):
    patient = get_field_value(instance, "Patient", default=None)
    return patient and patient.getPatientID() or ""


@indexer(IBatch)
def getPatientUID(instance):
    patient = get_field_value(instance, "Patient", default=None)
    return patient and api.get_uid(patient) or ""


@indexer(IBatch)
def getPatientTitle(instance):
    patient = get_field_value(instance, "Patient", default=None)
    return patient and patient.Title() or ""


@indexer(IBatch)
def getClientPatientID(instance):
    patient = get_field_value(instance, "Patient", default=None)
    return patient and patient.getClientPatientID() or ""


@indexer(IBatch)
def getDoctorID(instance):
    doctor = get_field_value(instance, "DoctorID", default=None)
    return doctor and api.get_id(doctor) or ""


@indexer(IBatch)
def getDoctorUID(instance):
    doctor = get_field_value(instance, "Doctor", default=None)
    return doctor and api.get_uid(doctor) or ""


@indexer(IBatch)
def getDoctorTitle(instance):
    doctor = get_field_value(instance, "Doctor", default=None)
    return doctor and doctor.Title() or ""
