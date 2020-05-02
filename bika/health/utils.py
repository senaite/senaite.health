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

from datetime import datetime

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.event import ObjectWillBeMovedEvent
from Products.ATContentTypes.utils import DT2dt
from dateutil.relativedelta import relativedelta
from zope.container.contained import notifyContainerModified
from zope.event import notify
from zope.i18n import translate
from zope.lifecycleevent import ObjectMovedEvent

from bika.health import bikaMessageFactory as _
from bika.health import logger
from bika.health.interfaces import IPatient
from bika.lims import api
from bika.lims.api import _marker
from bika.lims.interfaces import IBatch
from bika.lims.interfaces import IClient
from bika.lims.utils import chain
from bika.lims.utils import get_image
from bika.lims.utils import render_html_attributes
from bika.lims.utils import to_unicode
from bika.lims.utils import to_utf8


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
    field = instance.getField(field_name) or None
    if not field:
        if default is not _marker:
            return default
        api.fail("No field {} found for {}".format(field_name, repr(instance)))
    return field.get(instance)


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


def get_default_num_samples():
    """Returns the num of Samples (Columns) to be displayed in Sample Add Form
    """
    ar_count = api.get_setup().getDefaultNumberOfARsToAdd()
    return api.to_int(ar_count, 1)


def handle_after_submit(context, request, state):
    """Handles actions provided in extra_buttons slot from edit forms
    """
    status_id = "created"
    if request.get("form.button.new_sample"):
        # Redirect to Sample Add from Patient
        next_url = api.get_url(context)
        if IPatient.providedBy(context):
            uid = context.UID()
            client = context.getPrimaryReferrer()
            folder = client or api.get_portal().analysisrequests
            folder_url = api.get_url(folder)
            ar_count = get_default_num_samples()
            next_url = "{}/ar_add?Patient={}&ar_count={}".format(
                folder_url, uid, ar_count)

        # Redirect to Sample Add form from Batch
        elif IBatch.providedBy(context):
            ar_count = get_default_num_samples()
            next_url = "{}/ar_add?ar_count={}".format(next_url, ar_count)

        state.setNextAction('redirect_to:string:{}'.format(next_url))

    elif request.get("form.button.new_batch"):
        # Redirect to New Batch from Patient
        next_url = api.get_url(context)
        if IPatient.providedBy(context):
            # Create temporary Batch inside Patient context (the case will be
            # moved in client's folder later thanks to objectmodified event)
            next_url = "{}/createObject?type_name=Batch".format(next_url)
            #tmp_path = "portal_factory/Batch/{}".format(tmpID())
            #tmp_obj = context.restrictedTraverse(tmp_path)
            #batch_url = api.get_url(tmp_obj)
            #next_url = "{}/edit".format(batch_url)

        state.setNextAction('redirect_to:string:{}'.format(next_url))

    elif IPatient.providedBy(context):
        # Redirect to Patient's samples view
        next_url = "{}/analysisrequests".format(api.get_url(context))
        state.setNextAction('redirect_to:string:{}'.format(next_url))
    else:
        status_id = "success"
    return status_id


def get_age_ymd(birth_date, to_date=None):
    """Returns the age at to_date if not None. Otherwise, current age
    """
    delta = get_relative_delta(birth_date, to_date)
    return to_ymd(delta)


def get_relative_delta(from_date, to_date=None):
    """Returns the relative delta between two dates. If to_date is None,
    compares the from_date with now
    """
    from_date = to_datetime(from_date)
    if not from_date:
        raise TypeError("Type not supported: from_date")

    to_date = to_date or datetime.now()
    to_date = to_datetime(to_date)
    if not to_date:
        raise TypeError("Type not supported: to_date")

    return relativedelta(to_date, from_date)


def to_datetime(date_value, default=None, tzinfo=None):
    if isinstance(date_value, datetime):
        return date_value

    # Get the DateTime
    date_value = api.to_date(date_value, default=None)
    if not date_value:
        if default is None:
            return None
        return to_datetime(default, tzinfo=tzinfo)

    # Convert to datetime and strip
    return DT2dt(date_value).replace(tzinfo=tzinfo)


def to_ymd(delta):
    """Returns a representation of a relative delta in ymd format
    """
    if not isinstance(delta, relativedelta):
        raise TypeError("delta parameter must be a relative_delta")

    ymd = list("ymd")
    diff = map(str, (delta.years, delta.months, delta.days))
    age = filter(lambda it: int(it[0]), zip(diff, ymd))
    return " ".join(map("".join, age))


def move_obj(ob, destination):
    """
    This function has the same effect as:

        id = obj.getId()
        cp = origin.manage_cutObjects(id)
        destination.manage_pasteObjects(cp)

    but with slightly better performance and **without permission checks**. The
    code is mostly grabbed from OFS.CopySupport.CopyContainer_pasteObjects
    """
    id = ob.getId()

    # Notify the object will be copied to destination
    ob._notifyOfCopyTo(destination, op=1)

    # Notify that the object will be moved
    origin = aq_parent(aq_inner(ob))
    notify(ObjectWillBeMovedEvent(ob, origin, id, destination, id))

    # Effectively move the object from origin to destination
    origin._delObject(id, suppress_events=True)
    ob = aq_base(ob)
    destination._setObject(id, ob, set_owner=0, suppress_events=True)
    ob = destination._getOb(id)

    # Since we used "suppress_events=True", we need to manually notify that the
    # object has been moved and containers modified. This also makes the objects
    # to be re-catalogued
    notify(ObjectMovedEvent(ob, origin, id, destination, id))
    notifyContainerModified(origin)
    notifyContainerModified(destination)

    # Try to make ownership implicit if possible, so it acquires the permissions
    # from the container
    ob.manage_changeOwnershipType(explicit=0)
    return ob


def is_internal_client(client):
    """Returns whether the client passed in is an internal client
    """
    if not IClient.providedBy(client):
        raise TypeError("Type not supported")

    return api.get_parent(client) == api.get_portal().internal_clients


def is_external_client(client):
    """Returns whether the client passed is an external client
    """
    if not IClient.providedBy(client):
        raise TypeError("Type not supported")

    return api.get_parent(client) == api.get_portal().clients


def is_from_external_client(obj_or_brain):
    """Returns whether the object passed in belongs to an external client
    """
    clients = api.get_portal().clients
    return is_contained_by(clients, obj_or_brain)


def is_from_internal_client(obj_or_brain):
    """Returns whether the object passed in belongs to an internal client
    """
    internals = api.get_portal().internal_clients
    return is_contained_by(internals, obj_or_brain)


def is_contained_by(container_obj_or_brain, obj_or_brain):
    """Returns whether the container contains the obj passed in
    """
    base_path = api.get_path(container_obj_or_brain)
    obj_path = api.get_path(obj_or_brain)
    return base_path in obj_path


def is_logged_user_from_external_client():
    """Returns whether the current user belongs to an external client
    """
    client = api.get_current_client()
    if client and is_external_client(client):
        return True
    return False


def get_client_from_chain(obj):
    """Returns the client the obj belongs to, if any, by looking to the
    acquisition chain
    """
    if IClient.providedBy(obj):
        return obj

    for obj in chain(obj):
        if IClient.providedBy(obj):
            return obj
    return None


def is_shareable_type(portal_type):
    """Returns whether the portal_type passed in is shareable among internal
    clients
    """
    return portal_type in ["Patient", "Doctor", "Batch"]


def resolve_query_for_shareable(portal_type, context=None):
    """Resolves a query filter for the portal_type passed in and the context
    for which the query has to be filtered by
    """
    # Resolve the client from the object, if possible
    client = context and get_client_from_chain(context) or None

    if client and is_internal_client(client):
        # Client is internal and the portal type is "shareable", the query
        # must display all items of this portal_type that are located
        # inside any of the clients from "internal_clients" folder
        folder = api.get_portal().internal_clients
        return {
            "path": {"query": api.get_path(folder), "depth": 2},
            "portal_type": portal_type,
        }

    elif client:
        # Client is external. Only the items that belong to this client
        return {
            "path": {"query": api.get_path(client), "depth": 1},
            "portal_type": portal_type,
        }

    # We don't know neither the client nor the type of client
    return {"portal_type": portal_type}


def get_client_aware_html_image(obj):
    """Renders an icon based on the client the object belongs to
    """
    if is_from_external_client(obj):
        icon_info = ("lock.png", _("Private, from an external client"))

    elif is_from_internal_client(obj):
        if api.get_review_status(obj) == "shared":
            icon_info = ("share.png", _("Shared, from an internal client"))
        else:
            icon_info = ("share_lock.png",
                         _("From an internal client, but not shared"))
    else:
        logger.warn("No client assigned for {}".format(repr(obj)))
        icon_info = ("exclamation_red.png", _("No client assigned"))

    return get_html_image(icon_info[0], title=icon_info[1])


def get_all_granted_roles_for(folder, permission):
    """Returns a list of roles that have granted access to the folder. If the
    folder is acquire=1, it looks through all the hierarchy until acquire=0 to
    grab all the roles that effectively (regardless of acquire) has permission
    """
    roles = filter(lambda perm: perm.get('selected') == 'SELECTED',
                   folder.rolesOfPermission(permission))
    roles = map(lambda prole: prole['name'], roles)
    if api.is_portal(folder):
        return roles

    acquired = folder.acquiredRolesAreUsedBy(permission) == 'CHECKED' and 1 or 0
    if acquired:
        # Grab from the parent
        parent_roles = get_all_granted_roles_for(folder.aq_parent, permission)
        roles.extend(parent_roles)

    return list(set(roles))


def revoke_permission_for_role(folder, permission, role):
    """Revokes a permission for a given role and folder. It handles acquire
    gracefully
    """
    # Get all granted roles for this folder, regardless of acquire
    granted_roles = get_all_granted_roles_for(folder, permission)

    # Bail out the role from the list
    to_grant = filter(lambda name: name != role, granted_roles)
    if to_grant == granted_roles:
        # Nothing to do, the role does not have permission granted
        logger.info(
            "Role '{}' does not have permission {} granted for '{}' [SKIP]"
            .format(role, repr(permission), repr(folder))
        )
        return

    # Is this permission acquired?
    folder.manage_permission(permission, roles=to_grant, acquire=0)
    folder.reindexObject()
    logger.info("Revoked permission {} to role '{}' for '{}'"
                .format(repr(permission), role, repr(folder)))


def add_permission_for_role(folder, permission, role):
    """Grants a permission to the given role and given folder
    :param folder: the folder to which the permission for the role must apply
    :param permission: the permission to be assigned
    :param role: role to which the permission must be granted
    :return True if succeed, otherwise, False
    """
    roles = filter(lambda perm: perm.get('selected') == 'SELECTED',
                   folder.rolesOfPermission(permission))
    roles = map(lambda perm_role: perm_role['name'], roles)
    if role in roles:
        # Nothing to do, the role has the permission granted already
        logger.info(
            "Role '{}' has permission {} for {} already".format(role,
                                                                repr(permission),
                                                                repr(folder)))
        return False
    roles.append(role)
    acquire = folder.acquiredRolesAreUsedBy(permission) == 'CHECKED' and 1 or 0
    folder.manage_permission(permission, roles=roles, acquire=acquire)
    folder.reindexObject()
    logger.info(
        "Added permission {} to role '{}' for {}".format(repr(permission), role,
                                                         repr(folder)))
    return True
