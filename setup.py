from setuptools import setup, find_packages

version = '3.2.0.1711'

setup(name='bika.health',
      version=version,
      description="Bika Health Evo",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.rst").read()+ "\n",
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Zope2",
          "Intended Audience :: Healthcare Industry",
          "Intended Audience :: Information Technology",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
          "Programming Language :: Python",

      ],
      keywords=['lims', 'bika', 'opensource'],
      author='Naralabs',
      author_email='support@naralabs.com',
      url='https://github.com/naralabs/bika.lims',
      license='AGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bika'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'bika.lims',
          'archetypes.schemaextender',
          'collective.wtf',
      ],
      entry_points="""
          # -*- Entry points: -*-
          [z3c.autoinclude.plugin]
          target = plone
          """,
)
