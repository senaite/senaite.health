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

from Products.Archetypes.public import DisplayList
from bika.health import bikaMessageFactory as _

PROJECTNAME = "bika.health"
DEFAULT_PROFILE_ID = "profile-{}:default".format(PROJECTNAME)

GENDERS = DisplayList((
    ('male', _('Male')),
    ('female', _('Female')),
    ('dk', _("Don't Know")),
    ))

ETHNICITIES = DisplayList((
    ('Native American', _('Native American')),
    ('Asian', _('Asian')),
    ('Black', _('Black')),
    ('Native Hawaiian or Other Pacific Islander', _('Native Hawaiian or Other Pacific Islander')),
    ('White', _('White')),
    ('Hispanic or Latino', _('Hispanic or Latino')),
))

GENDERS_APPLY = DisplayList((
    ('male', _('Male')),
    ('female', _('Female')),
    ('dk', _("Both")),
))

MENSTRUAL_STATUSES = DisplayList((
    ('regular', _('Regular')),
    ('irregular', _('Irregular')),
    ('none', _('No menstrual cycle')),
))
