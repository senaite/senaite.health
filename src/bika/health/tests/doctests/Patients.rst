Patients
========

Patients can belong to Internal Clients or (External) Clients and the Client
field is mandatory.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t Patients


Test Setup
----------

Needed imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from Products.CMFCore.permissions import View
    >>> from bika.lims import api

Variables:

    >>> portal = self.portal
    >>> request = self.request

Create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> i_client = api.create(portal.internal_clients, "Client", Name="Internal client", ClientID="HH", MemberDiscountApplies=True)


Patient Creation and Client assignment
--------------------------------------

The creation of a Patient inside Patients folder is not allowed. The Patients
folder is only used as a shortcut to view Patients registered in the system:

    >>> patients = portal.patients
    >>> api.create(patients, "Patient")
    Traceback (most recent call last):
    [...]
    AttributeError: 'NoneType' object has no attribute '_setObject'

If we create a Patient inside an External Client, the object is automatically
transitioned to "active" status:

    >>> patient = api.create(client, "Patient")
    >>> patient
    <Patient at /plone/clients/client-1/P000002>

    >>> patient.getClient()
    <Client at /plone/clients/client-1>

    >>> api.get_review_status(patient)
    'active'

And in "active" status, neither users with role `InternalClient` nor `Client`
do have permission View granted:

    >>> allowed = set(rolesForPermissionOn(View, patient))
    >>> "InternalClient" in allowed
    False
    >>> "Client" in allowed
    False

A Patient from an external client cannot be shared/unshared:

    >>> isTransitionAllowed(patient, "share")
    False
    >>> isTransitionAllowed(patient, "unshare")
    False

If we create a Patient inside an Internal Client, the object is transitioned to
"shared" status by default:

    >>> patient = api.create(i_client, "Patient")
    >>> patient
    <Patient at /plone/internal_clients/client-2/P000003>

    >>> patient.getClient()
    <Client at /plone/internal_clients/client-2>

    >>> api.get_review_status(patient)
    'shared'

And in "shared" status, while users with role `InternalClient` have permission
View, users with role `Client` don't:

    >>> allowed = set(rolesForPermissionOn(View, patient))
    >>> "InternalClient" in allowed
    True
    >>> "Client" in allowed
    False

A Patient from an internal client cannot be unshared/activated:

    >>> isTransitionAllowed(patient, "unshare")
    False
    >>> isTransitionAllowed(patient, "activate")
    False
