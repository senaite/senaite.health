.. figure:: https://raw.githubusercontent.com/senaite/senaite.health/master/static/senaite-health-logo.png
   :width: 500px
   :alt: senaite.core
   :align: center

— **SENAITE.HEALTH**: *SENAITE for healthcare labs, the evolution of Bika Health*

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


Introduction
============

SENAITE.HEALTH is an Open Source Laboratory Information System (LIS) suitable
for Health Care Laboratories, focused on patient and clinical cases.

SENAITE.HEALTH is an extension for `SENAITE.CORE <https://github.com/senaite/senaite.core>`_,
an Open Source LIMS for enterprise environments, especially focused to behave
with high speed, excellent performance and good stability.

This software is a derivative work of BikaHealth_ software and comes with the same user 
interface.


Installation
============

SENAITE.HEALTH is built on top of `Plone CMS <https://plone.org>`_, so it must be
installed first.
Please, follow the `installation instructions for Plone 4.x <https://docs.plone.org/4/en/manage/installing/installation.html>`_
first.

Once Plone 4.x is installed successfully, you can choose any of the two options
below:

Ready-to-go installation
------------------------
With this installation modality, the sources from ``senaite.health`` will be
downloaded automatically from `Python Package Index (Pypi) <https://pypi.python.org/pypi/senaite.health>`_.
If you want the latest code from the `source code repository <https://github.com/senaite/senaite.health>`_,
follow the `installation instructions for development <https://github.com/senaite/senaite.health/blob/master/README.rst#installation-for-development>`_.

Create a new buildout file ``senaite.cfg`` which extends your existing
``buildout.cfg`` – this way you can easily keep development stuff separate from
your main buildout.cfg which you can also use on the production server::

  [buildout]
  index = https://pypi.python.org/simple
  extends = buildout.cfg

  [instance]
  eggs +=
      senaite.health

Note that with this approach you do not need to modify the existing buildout.cfg
file.

Then build it out with this special config file::

  bin/buildout -c senaite.cfg

and buildout will automatically download and install all required dependencies.

For further details about Buildout and how to install add-ons for Plone, please check
`Installing add-on packages using Buildout from Plone documentation <https://docs.plone.org/4/en/manage/installing/installing_addons.html>`_.


Installation for development
----------------------------

This is the recommended approach how to enable ``senaite.health`` for your
development environment. With this approach, you'll be able to download the
latest source code from `senaite.health's repository <https://github.com/senaite/senaite.health>`_
and contribute as well.

Use git to fetch ``senaite.health`` source code to your buildout environment::

  cd src
  git clone git://github.com/senaite/senaite.health.git senaite.health

Create a new buildout file ``senaite.cfg`` which extends your existing
``buildout.cfg`` – this way you can easily keep development stuff separate
from your main buildout.cfg which you can also use on the production server.

``senaite.cfg``::

  [buildout]
  index = https://pypi.python.org/simple
  extends = buildout.cfg
  develop +=
      src/senaite.health

  [instance]
  eggs +=
      senaite.health

Note that with this approach you do not need to modify the existing buildout.cfg
file.

Then build it out with this special config file::

  bin/buildout -c senaite.cfg

and buildout will automatically download and install all required dependencies.


Contribute
==========

We want contributing to SENAITE.HEALTH to be fun, enjoyable, and educational for
anyone, and everyone. This project adheres to the `Contributor Covenant <https://github.com/senaite/senaite.health/blob/master/CODE_OF_CONDUCT.md>`_.
By participating, you are expected to uphold this code. Please report
unacceptable behavior.

Contributions go far beyond pull requests and commits. Although we love giving
you the opportunity to put your stamp on SENAITE.HEALTH, we also are thrilled to
receive a variety of other contributions. Please, read `Contributing to senaite.core
document <https://github.com/senaite/senaite.health/blob/master/CONTRIBUTING.md>`_.


Feedback and support
====================

* `Gitter channel <https://gitter.im/senaite/Lobby>`_
* `Users list <https://sourceforge.net/projects/senaite/lists/senaite-users>`_


License
=======
SENAITE.HEALTH
Copyright (C) 2018 Senaite Foundation

This software, henceforth "SENAITE.HEALTH", an add-on for
`Plone software <https://plone.org/>`_, is a derivative work of BikaHealth_.

This program is free software; you can redistribute it and/or
modify it under the terms of the `GNU General Public License version 2 <./LICENSE>`_
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.



.. Links

.. _BIKAHEALTH: https://github.com/bikalims/bika.health
