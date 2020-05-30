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

from bika.health import logger
from bika.health.utils import is_internal_client
from bika.lims.interfaces import IClient


def _linkUser(self, user):
    """Set the UID of the current Contact in the User properties and update
    all relevant own properties.
    """
    logger.warn("MONKEY PATCHING __linkUser")
    KEY = "linked_contact_uid"

    username = user.getId()
    contact = self.getContactByUsername(username)

    # User is linked to another contact (fix in UI)
    if contact and contact.UID() != self.UID():
        raise ValueError("User '{}' is already linked to Contact '{}'"
                         .format(username, contact.Title()))

    # User is linked to multiple other contacts (fix in Data)
    if isinstance(contact, list):
        raise ValueError("User '{}' is linked to multiple Contacts: '{}'"
                         .format(username, ",".join(
            map(lambda x: x.Title(), contact))))

    # XXX: Does it make sense to "remember" the UID as a User property?
    tool = user.getTool()
    try:
        user.getProperty(KEY)
    except ValueError:
        logger.info("Adding User property {}".format(KEY))
        tool.manage_addProperty(KEY, "", "string")

    # Set the UID as a User Property
    uid = self.UID()
    user.setMemberProperties({KEY: uid})
    logger.info("Linked Contact UID {} to User {}".format(
        user.getProperty(KEY), username))

    # Set the Username
    self.setUsername(user.getId())

    # Update the Email address from the user
    self.setEmailAddress(user.getProperty("email"))

    # somehow the `getUsername` index gets out of sync
    self.reindexObject()

    # N.B. Local owner role and client group applies only to client
    #      contacts, but not lab contacts.
    if IClient.providedBy(self.aq_parent):
        # Grant local Owner role
        self._addLocalOwnerRole(username)
        # Add user to "Clients" group
        self._addUserToGroup(username, group="Clients")

        # SENAITE.HEALTH-specific!
        # Add user to "InternalClients" group
        if is_internal_client(self.aq_parent):
            self._addUserToGroup(username, group="InternalClients")

    return True


def _unlinkUser(self):
    """Remove the UID of the current Contact in the User properties and
    update all relevant own properties.
    """
    logger.warn("MONKEY PATCHING __unlinkUser")
    KEY = "linked_contact_uid"

    # Nothing to do if no user is linked
    if not self.hasUser():
        return False

    user = self.getUser()
    username = user.getId()

    # Unset the UID from the User Property
    user.setMemberProperties({KEY: ""})
    logger.info("Unlinked Contact UID from User {}"
                .format(user.getProperty(KEY, "")))

    # Unset the Username
    self.setUsername(None)

    # Unset the Email
    self.setEmailAddress(None)

    # somehow the `getUsername` index gets out of sync
    self.reindexObject()

    # N.B. Local owner role and client group applies only to client
    #      contacts, but not lab contacts.
    if IClient.providedBy(self.aq_parent):
        # Revoke local Owner role
        self._delLocalOwnerRole(username)
        # Remove user from "Clients" group
        self._delUserFromGroup(username, group="Clients")

        # SENAITE.HEALTH-specific!
        # Remove user from "InternalClients" group
        if is_internal_client(self.aq_parent):
            self._delUserFromGroup(username, group="InternalClients")

    return True