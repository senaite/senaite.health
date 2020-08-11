# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2017-2019 by it's authors

from setuptools import setup, find_packages


version = '1.2.4'

setup(
    name='senaite.health',
    version=version,
    description="SENAITE Health",
    long_description=open("README.rst").read() + "\n" +
    open("CHANGES.rst").read() + "\n",
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
    ],
    keywords=['lims', 'lis', 'senaite', 'opensource', 'health'],
    author="RIDING BYTES & NARALABS",
    author_email="senaite@senaite.com",
    url='https://github.com/senaite/senaite.health',
    license='GPLv2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['bika'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "archetypes.schemaextender",
        "senaite.lims>=1.3.4",
        "senaite.lims<1.4.0",
        "senaite.panic",
    ],
    extras_require={
        'test': [
            'unittest2',
            'plone.app.testing',
        ]
    },
    entry_points="""
        # -*- Entry points: -*-
        [z3c.autoinclude.plugin]
        target = plone
        """,
)
