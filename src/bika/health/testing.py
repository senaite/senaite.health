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

from bika.lims.exportimport.load_setup_data import LoadSetupData
from plone.app.testing import (PLONE_FIXTURE, SITE_OWNER_NAME,
                               FunctionalTesting, PloneSandboxLayer, login,
                               logout)
from plone.testing import z2


from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.setuphandlers import setupPortalContent
from Testing.makerequest import makerequest

import Products.ATExtensions
import collective.js.jqueryui
import plone.app.iterate


class BaseLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import bika.lims
        import bika.health
        import archetypes.schemaextender
        # Load ZCML
        self.loadZCML(package=Products.ATExtensions)
        self.loadZCML(package=plone.app.iterate)
        self.loadZCML(package=collective.js.jqueryui)
        self.loadZCML(package=archetypes.schemaextender)
        self.loadZCML(package=bika.lims)
        self.loadZCML(package=bika.health)

        # Required by Products.CMFPlone:plone-content
        z2.installProduct(app, 'Products.PythonScripts')
        z2.installProduct(app, 'bika.lims')
        z2.installProduct(app, 'bika.health')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'bika.lims:default')
        self.applyProfile(portal, 'bika.health:default')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'bika.lims')
        z2.uninstallProduct(app, 'bika.health')
        z2.uninstallProduct(app, 'Products.PythonScripts')


class DataLayer(BaseLayer):
    """Layer including Demo Data
    """

    def setup_data_load(self, portal, request):
        login(portal.aq_parent, SITE_OWNER_NAME)

        wf = getToolByName(portal, 'portal_workflow')
        wf.setDefaultChain('plone_workflow')
        setupPortalContent(portal)

        # make sure we have folder_listing as a template
        portal.getTypeInfo().manage_changeProperties(
            view_methods=['folder_listing'],
            default_view='folder_listing')
        # Add some test users
        for role in ('LabManager',
                     'LabClerk',
                     'Analyst',
                     'Verifier',
                     'Sampler',
                     'Preserver',
                     'Publisher',
                     'Member',
                     'Reviewer',
                     'RegulatoryInspector'):
            for user_nr in range(2):
                if user_nr == 0:
                    username = "test_%s" % (role.lower())
                else:
                    username = "test_%s%s" % (role.lower(), user_nr)
                member = portal.portal_registration.addMember(
                    username,
                    username,
                    properties={
                        'username': username,
                        'email': username + "@example.com",
                        'fullname': username}
                )
                # Add user to all specified groups
                group_id = role + "s"
                group = portal.portal_groups.getGroupById(group_id)
                if group:
                    group.addMember(username)
                # Add user to all specified roles
                member._addRole(role)
                # If user is in LabManagers, add Owner local role on clients folder
                if role == 'LabManager':
                    portal.clients.manage_setLocalRoles(username, ['Owner', ])

        # load test data
        request = makerequest(portal.aq_parent).REQUEST
        request.form['setupexisting'] = 1
        request.form['existing'] = "bika.health:test"
        lsd = LoadSetupData(portal, request)
        lsd()

        logout()

    def setUpPloneSite(self, portal):
        super(DataLayer, self).setUpPloneSite(portal)

        # Install Demo Data
        self.setup_data_load(portal, portal.REQUEST)


BASE_LAYER_FIXTURE = BaseLayer()
BASE_TESTING = FunctionalTesting(
    bases=(BASE_LAYER_FIXTURE,), name="SENAITE.HEALTH:BaseTesting")

DATA_LAYER_FIXTURE = DataLayer()
DATA_TESTING = FunctionalTesting(
    bases=(DATA_LAYER_FIXTURE,), name="SENAITE.HEALTH:DataTesting")
