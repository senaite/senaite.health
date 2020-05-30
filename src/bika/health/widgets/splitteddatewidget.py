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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from Products.CMFPlone.i18nl10n import ulocalized_time
import json


class SplittedDateWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'ulocalized_time': ulocalized_time,
        'macro': "bika_health_widgets/splitteddatewidget",
        'helper_js': ("bika_health_widgets/splitteddatewidget.js",),
        'helper_css': ("bika_health_widgets/splitteddatewidget.css",),
        'changeYear': True,
        'changeMonth': True,
        'changeDay': True,
        'maxDate': '+0d',
        'yearRange': '-100:+0'
    })
    security = ClassSecurityInfo()

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        outvalues = [{'year': form.get('PatientAgeAtCaseOnsetDate_year', empty_marker),
                     'month': form.get('PatientAgeAtCaseOnsetDate_month', empty_marker),
                     'day': form.get('PatientAgeAtCaseOnsetDate_day', empty_marker)}]
        return outvalues, {}

    def jsondumps(self, val):
        return json.dumps(val)


registerWidget(SplittedDateWidget,
               title='SplittedDateWidget',
               description=('Simple control with three input fields (year, month, day)'),
               )
