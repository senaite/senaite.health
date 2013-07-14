from bika.health.testing import HEALTH_ROBOT_TESTING
from plone.testing import layered

import robotsuite
import unittest


ROBOT_TESTS = [
    'test_regulatoryinspector.robot',
]


def test_suite():
    suite = unittest.TestSuite()
    for RT in ROBOT_TESTS:
        suite.addTests([
            layered(robotsuite.RobotTestSuite(RT), layer=HEALTH_ROBOT_TESTING)
        ])
    return suite
