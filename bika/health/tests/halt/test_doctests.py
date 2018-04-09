# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import doctest
import unittest

from plone.testing import layered
from bika.health.testing import BASE_TESTING

OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

DOCTESTS = [
]


def test_suite():
    suite = unittest.TestSuite()
    for module in DOCTESTS:
        suite.addTests([
            layered(
                doctest.DocTestSuite(
                    module=module,
                    optionflags=OPTIONFLAGS
                ),
                layer=BASE_TESTING
            ),
        ])
    return suite
