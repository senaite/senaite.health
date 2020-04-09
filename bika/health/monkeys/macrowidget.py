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

from AccessControl.unauthorized import Unauthorized


def __call__(self, mode, instance, context=None):
    self.bootstrap(instance)
    # If an attribute called macro_<mode> exists resolve that
    # before the generic macro, this lets other projects
    # create more partial widgets
    macro = getattr(self, 'macro_%s' % mode, self.macro)

    # Now split the macro into optional parts using '|'
    # if the first part doesn't exist, the search continues
    paths = macro.split('|')
    if len(paths) == 1 and macro == self.macro:
        # Prepend the default (optional) customization element
        paths.insert(0, 'at_widget_%s' % self.macro.split('/')[-1])
    for path in paths:
        try:
            template = instance.restrictedTraverse(path=path)
            if template:
                return template.macros[mode]
        except (Unauthorized, AttributeError, KeyError):
            # This means we didn't have access or it doesn't exist
            pass
    raise AttributeError("Macro %s does not exist for %s" % (macro,
                                                             instance))
