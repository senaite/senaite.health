from setuptools import setup, find_packages
import os

version = '3.1.5'

setup(name='bika.health',
      version=version,
      description="Bika Health Open Source LIMS",
      long_description=open("README.md").read() + "\n\n" +
                       open("CHANGELOG.txt").read(),
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        ],
      keywords=['lims', 'health', 'bika', 'opensource'],
      author='Bika Laboratory Systems',
      author_email='support@bikalabs.com',
      maintainer='Naralabs',
      maintainer_email='info@naralabs.com',
      url='http://github.com/bikalabs/bika.health',
      license='AGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bika'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'bika.lims>=3.1.5',
          'archetypes.schemaextender',
          'collective.wtf',
      ],
      extras_require={
          'test': [
                  'plone.app.testing',
                  'robotsuite',
                  'robotframework-selenium2library',
                  'plone.app.robotframework',
                  'robotframework-debuglibrary',
              ]
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
