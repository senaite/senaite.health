Cases
=====

Cases can belong to Internal Clients or (External) Clients and the Client field
is mandatory.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t Cases


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


Case Creation and Client assignment
-----------------------------------

If we create a Case inside an External Client, the object is automatically
transitioned to "open" status:

    >>> case = api.create(client, "Batch")
    >>> case
    <Batch at /plone/clients/client-1/B-001>

    >>> case.getClient()
    <Client at /plone/clients/client-1>

    >>> api.get_review_status(case)
    'open'

And in "open" status, neither users with role `InternalClient` nor `Client`
do have permission View granted:

    >>> allowed = set(rolesForPermissionOn(View, case))
    >>> "InternalClient" in allowed
    False
    >>> "Client" in allowed
    False

A Case from an external client cannot be shared/unshared:

    >>> isTransitionAllowed(case, "share")
    False
    >>> isTransitionAllowed(case, "unshare")
    False

If we create a Case inside an Internal Client, the object is transitioned to
"shared" status by default:

    >>> case = api.create(i_client, "Batch")
    >>> case
    <Batch at /plone/internal_clients/client-2/B-002>

    >>> case.getClient()
    <Client at /plone/internal_clients/client-2>

    >>> api.get_review_status(case)
    'shared'

And in "shared" status, while users with role `InternalClient` have permission
View, users with role `Client` don't:

    >>> allowed = set(rolesForPermissionOn(View, case))
    >>> "InternalClient" in allowed
    True
    >>> "Client" in allowed
    False

A Case from an internal client cannot be unshared/reinstate:

    >>> isTransitionAllowed(case, "unshare")
    False
    >>> isTransitionAllowed(case, "reinstate")
    False
