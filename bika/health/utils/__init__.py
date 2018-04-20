# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.api import _marker


def get_obj_from_field(instance, fieldname, default=_marker):
    """ Get an object from a Reference Field of any instance
    :param fieldname: Reference Field Name
    :return:
    """
    if not fieldname:
        return default
    field = instance.getField(fieldname, None)
    if not field:
        if default is not _marker:
            return default
        api.fail("{} doesn't have field called {} ".format(repr(instance),
                                                           fieldname))
    return field.get(instance)


def get_attr_from_field(instance, fieldname, attrname, default=None):
    item = get_obj_from_field(instance, fieldname, None)
    if not item:
        return default
    return api.safe_getattr(item, attr=attrname, default=default)
