# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.WorkflowCore import WorkflowException
from bika.lims.utils import getHiddenAttributesForClass
from types import DictType
from Products.CMFCore.utils import getToolByName
from bika.lims.interfaces import IATWidgetVisibility
from zope.interface import implements
from bika.health.permissions import ViewPatients

_marker = []


class PatientFieldsWidgetVisibility(object):
    """This will force readonly fields to be uneditable, and viewable only by
     those with ViewPatients permission.
    """
    implements(IATWidgetVisibility)

    def __init__(self, context):
        self.context = context
        # self.sort = 100

    def __call__(self, context, mode, field, default):
        state = default if default else 'invisible'

        header_table_fields = ['Patient',
                               'PatientID',
                               'ClientPatientID']
        readonly_fields = ['Batch',
                           'Patient',
                           'PatientID',
                           'ClientPatientID']

        mtool = getToolByName(self.context, 'portal_membership')
        has_perm = mtool.checkPermission(ViewPatients, self.context)

        fieldName = field.getName()
        if fieldName not in header_table_fields and fieldName not in readonly_fields:
            return state

        #from bika.health import logger
        #oldstate = state
        if has_perm:
           if mode == 'header_table' and fieldName in header_table_fields:
               state = 'visible'
           if mode == 'view' and fieldName in readonly_fields:
               state = 'visible'
        if mode == 'edit' and fieldName in readonly_fields:
               state = 'invisible'
        #if state != oldstate:
        #    logger.info("PatientFieldsWidgetVisibility %s %s %s %s->%s"%(self.context, has_perm, fieldName, oldstate, state))

        return state
