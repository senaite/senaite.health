Patients
========

Patients are one of the objects from senaite.health that are not present
in senaite.core.


Running this test from the buildout directory::

    bin/test test_textual_doctests -t Patients


Test Setup
----------

Needed imports:

.. code::

    >>> from bika.lims import api

Variables:

.. code::

    >>> portal = self.portal
    >>> request = self.request
    >>> bika_setup = portal.bika_setup
    >>> patients = bika_setup.patients


We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager:

.. code::

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Patient Creation
----------------

Create a Patient:

.. code::

    >>> patient = api.create(patients, "Patient")
    >>> patient
    <Patient at /plone/patients/P000001>

