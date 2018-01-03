from setuptools import setup, find_packages

version = '1.0.0'

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
          "Programming Language :: Python",

      ],
      keywords=['lims', 'lis', 'bika', 'senaite', 'opensource', 'health'],
      author='SENAITE Foundation',
      author_email='support@senaite.com',
      url='https://github.com/senaite/bika.health',
      license='GPLv2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bika'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'senaite.core',
          'archetypes.schemaextender',
          'collective.wtf',
      ],
      entry_points="""
          # -*- Entry points: -*-
          [z3c.autoinclude.plugin]
          target = plone
          """,
)
