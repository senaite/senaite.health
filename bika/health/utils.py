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

from bika.health import logger
from bika.lims import api
from bika.lims.api import _marker
from bika.lims.utils import render_html_attributes, to_utf8, to_unicode
from zope.i18n import translate


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


def get_html_image(name, **kwargs):
    """Returns a well-formed img html
    :param name: file name of the image
    :param kwargs: additional attributes and values
    :return: a well-formed html img
    """
    if not name:
        return ""
    attr = render_html_attributes(**kwargs)
    return '<img src="{}" {}/>'.format(get_resource_url(name), attr)


def get_resource_url(resource, route="++resource++bika.health.images"):
    """Returns the url for the given resource name
    """
    portal_url = api.get_url(api.get_portal())
    return "{}/{}/{}".format(portal_url, route, resource)


def translate_i18n(i18n_msg):
    """Safely translate and convert to UTF8, any zope i18n msgid returned from
    senaite health's message factory
    """
    text = to_unicode(i18n_msg)
    try:
        request = api.get_request()
        domain = getattr(i18n_msg, "domain", "senaite.health")
        text = translate(text, domain=domain, context=request)
    except UnicodeDecodeError:
        logger.warn("{} couldn't be translated".format(text))
    return to_utf8(text)


def get_field_value(instance, field_name, default=_marker):
    """Returns the value of a Schema field from the instance passed in
    """
    instance = api.get_object(instance)
    field = instance.Schema() and instance.Schema().getField(field_name) or None
    if not field:
        if default is not _marker:
            return default
        api.fail("No field {} found for {}".format(field_name, repr(instance)))
    return instance.Schema().getField(field_name).get(instance)


def set_field_value(instance, field_name, value):
    """Sets the value to a Schema field
    """
    if field_name == "id":
        logger.warn("Assignment of id is not allowed")
        return
    logger.info("Field {} = {}".format(field_name, repr(value)))
    instance = api.get_object(instance)
    field = instance.Schema() and instance.Schema().getField(field_name) or None
    if not field:
        api.fail("No field {} found for {}".format(field_name, repr(instance)))
    field.set(instance, value)
