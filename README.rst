.. figure:: https://raw.githubusercontent.com/senaite/senaite.health/master/static/senaite-health-logo.png
   :width: 500px
   :alt: senaite.health
   :align: center


*SENAITE LIMS extension for Health care labs*
=============================================

.. image:: https://img.shields.io/pypi/v/senaite.health.svg?style=flat-square
    :target: https://pypi.python.org/pypi/senaite.health

.. image:: https://travis-ci.org/senaite/senaite.health.svg?branch=master
    :target: https://travis-ci.org/senaite/senaite.health

.. image:: https://img.shields.io/scrutinizer/g/senaite/senaite.health/master.svg?style=flat-square
    :target: https://scrutinizer-ci.com/g/senaite/senaite.health/

.. image:: https://img.shields.io/github/issues-pr/senaite/senaite.health.svg?style=flat-square
    :target: https://github.com/seniate/senaite.health/pulls

.. image:: https://img.shields.io/github/issues/senaite/senaite.health.svg?style=flat-square
    :target: https://github.com/senaite/senaite.health/issues

.. image:: https://img.shields.io/github/contributors/senaite/senaite.health.svg?style=flat-square
    :target: https://github.com/senaite/senaite.health/blob/master/CONTRIBUTORS.rst

.. image:: https://img.shields.io/badge/Built%20with-%E2%9D%A4-red.svg
   :target: https://github.com/senaite/senaite.health

.. image:: https://img.shields.io/badge/Made%20for%20SENAITE-%E2%AC%A1-lightgrey.svg
   :target: https://www.senaite.com


Introduction
============

SENAITE.HEALTH is an extension for `SENAITE.LIMS
<https://github.com/senaite/senaite.lims>`_ to make it suitable for Health Care
Laboratories, with additional capabilities for the management of patients,
doctors, clinical cases, symptoms, and a lot more.


Installation
============

Please follow the `installation instructions for SENAITE LIMS
<https://www.senaite.com/docs/installation>`_ first.

After SENAITE LIMS is installed, stop the instance and add `senaite.health`
into the `eggs` list inside the `[buildout]` section of your `buildout.cfg`::

   [buildout]
   eggs =
       Plone
       Pillow
       senaite.lims
       senaite.health

For the changes to take effect you need to re-run buildout from your console::

   $ bin/buildout

Start the instance and login as admin user. Go to Site Setup > Add-ons, select
"SENAITE HEALTH" and press Install.


Screenshots
===========

Dashboard
---------

.. image:: https://raw.githubusercontent.com/senaite/senaite.health/master/static/dashboard.png
   :alt: Dashboard
   :width: 760px
   :align: center


Analyses
--------

.. image:: https://raw.githubusercontent.com/senaite/senaite.health/master/static/analyses.png
   :alt: Analsyes
   :width: 760px
   :align: center

Patients
--------

.. image:: https://raw.githubusercontent.com/senaite/senaite.health/master/static/patients.png
   :alt: Patients
   :width: 760px
   :align: center

Cases
-----

.. image:: https://raw.githubusercontent.com/senaite/senaite.health/master/static/cases.png
   :alt: Cases
   :width: 760px
   :align: center


Aetiologic Agents
-----------------

.. image:: https://raw.githubusercontent.com/senaite/senaite.health/master/static/aetiologic_agents.png
   :alt: Aetiologic agents
   :width: 760px
   :align: center


Contribute
==========

We want contributing to SENAITE.HEALTH to be fun, enjoyable, and educational for
anyone, and everyone. This project adheres to the `Contributor Covenant
<https://github.com/senaite/senaite.health/blob/master/CODE_OF_CONDUCT.md>`_.

By participating, you are expected to uphold this code. Please report
unacceptable behavior.

Contributions go far beyond pull requests and commits. Although we love giving
you the opportunity to put your stamp on SENAITE.HEALTH, we also are thrilled to
receive a variety of other contributions.

Please, read `Contributing to senaite.health document
<https://github.com/senaite/senaite.health/blob/master/CONTRIBUTING.md>`_.

If you wish to contribute with translations, check the project site on
`Transifex <https://www.transifex.com/senaite/senaite-health/>`_.


Feedback and support
====================

* `Community site <https://community.senaite.org/>`_
* `Gitter channel <https://gitter.im/senaite/Lobby>`_
* `Users list <https://sourceforge.net/projects/senaite/lists/senaite-users>`_


License
=======

**SENAITE.HEALTH** Copyright (C) 2018-2020 RIDING BYTES & NARALABS

This software, henceforth "SENAITE.HEALTH" is an add-on for
`Plone CMS <https://plone.org/>`_ and is a derivative work of BIKA HEALTH.

This program is free software; you can redistribute it and/or modify it under
the terms of the `GNU General Public License version 2
<https://github.com/senaite/senaite.core/blob/master/LICENSE>`_ as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
