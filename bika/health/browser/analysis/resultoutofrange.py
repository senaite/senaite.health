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

from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IFieldIcons
from zope.interface import implements
from zope.component import adapts


class ResultOutOfRange(object):
    """An alert provider for Analysis results outside of panic ranges
    """

    implements(IFieldIcons)
    adapts(IAnalysis)

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, specification=None, **kwargs):
        """ Check if result value is 'in panic'.
        """
        analysis = self.context
        path = '++resource++bika.health.images'

        translate = self.context.translate
        workflow = getToolByName(self.context, 'portal_workflow')

        astate = workflow.getInfoFor(analysis, 'review_state')
        if astate == 'retracted':
            return {}

        result = result is not None and str(result) or analysis.getResult()
        if result == '':
            return {}
        # if analysis result is not a number, then we assume in range
        try:
            result = float(str(result))
        except ValueError:
            return {}
        # No specs available, assume in range
        specs = analysis.getAnalysisSpecs(specification) \
            if hasattr(analysis, 'getAnalysisSpecs') else None
        if specs is None:
            return {}

        keyword = analysis.getKeyword()
        spec = specs.getResultsRangeDict()
        if keyword in spec:
            try:
                spec_min = float(spec[keyword]['minpanic'])
            except (ValueError, TypeError):
                spec_min = None

            try:
                spec_max = float(spec[keyword]['maxpanic'])
            except (ValueError, TypeError):
                spec_max = None

            if not (spec_min or spec_max):
                # No min and max values defined
                outofrange, acceptable, o_spec = False, None, None

            elif spec_min and spec_max and spec_min <= result <= spec_max:
                # min and max values defined
                outofrange, acceptable, o_spec = False, None, None

            elif spec_min and not spec_max and spec_min <= result:
                # max value not defined
                outofrange, acceptable, o_spec = False, None, None

            elif not spec_min and spec_max and spec_max >= result:
                # min value not defined
                outofrange, acceptable, o_spec = False, None, None

            else:
                outofrange, acceptable, o_spec = True, False, spec[keyword]

        else:
            # Analysis without specification values. Assume in range
            outofrange, acceptable, o_spec = False, None, None

        alerts = {}
        if outofrange:
            range_str = "{0} {1}, {2} {3}".format(
                translate(_("minpanic")), str(o_spec['minpanic']),
                translate(_("maxpanic")), str(o_spec['maxpanic'])
            )

            if acceptable:
                message = "{0} ({1})".format(
                    translate(_('Result in shoulder panic range')), range_str)
            else:
                message = "{0} ({1})".format(
                    translate(_('Result exceeded panic level')), range_str)

            alerts[analysis.UID()] = [{
                'msg': message,
                'icon': path + '/lifethreat.png',
                'field': 'Result', }, ]
        return alerts
