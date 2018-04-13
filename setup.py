from setuptools import setup, find_packages

version = '1.1.2'

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
    author='SENAITE Foundation',
    author_email='support@senaite.com',
    url='https://github.com/senaite/senaite.core',
    license='GPLv2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['bika'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'senaite.core',
        'archetypes.schemaextender',
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
