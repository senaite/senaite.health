# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
