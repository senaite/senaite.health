from setuptools import setup, find_packages

version = '0.1'

setup(name='bika.health',
      version=version,
      description="Bika LIMS Health branch",
      long_description=open("README.md").read(),
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Bika Open Source LIMS',
      author='Bika Laboratory Systems',
      author_email='support@bikalabs.com',
      url='www.bikalabs.com',
      license='AGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bika'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'bika.lims',
          'archetypes.schemaextender',
          'collective.wtf',
      ],
      extras_require={
          'test': [
                  'plone.app.testing',
                  'robotsuite',
                  'robotframework-selenium2library',
                  'plone.app.robotframework'
              ]
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
