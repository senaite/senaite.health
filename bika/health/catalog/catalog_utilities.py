# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.health.catalog.analysisrequest_catalog import\
    analysisrequest_catalog_definition
from bika.health.catalog.patient_catalog import patient_catalog_definition
from bika.lims import deprecated


def getCatalogDefinitions():
    """
    Returns a dictionary with catalog definitions
    """
    return patient_catalog_definition


def getCatalogExtensions():
    """
    Returns a dictionary with catalog extensions
    """
    return analysisrequest_catalog_definition


# TODO-catalog: Function to review its use. Good candidate to be removed
@deprecated('Flagged in 17.03')
def getCatalog(instance, field='UID'):
    """ Return the catalog which indexes objects of instance's type.
    If an object is indexed by more than one catalog, the first match
    will be returned.
    """
    uid = instance.UID()
    if 'workflow_skiplist' in instance.REQUEST \
            and [x for x in instance.REQUEST['workflow_skiplist']
                 if x.find(uid) > -1]:
        return None
    else:
        # grab the first catalog we are indexed in.
        # we're only indexed in one.
        at = getToolByName(instance, 'archetype_tool')
        plone = instance.portal_url.getPortalObject()
        catalog_name = instance.portal_type in at.catalog_map \
            and at.catalog_map[instance.portal_type][0] or 'portal_catalog'

        catalog = getToolByName(plone, catalog_name)
        return catalog
