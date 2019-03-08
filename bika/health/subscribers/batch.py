from bika.lims import workflow as wf
from bika.lims import api
from bika.lims.api import security


def ObjectInitializedEventHandler(batch, event):
    """Actions to be done when a batch is created. If a client has been
    assigned to the batch, this function assigns the role "Owner" for the
    batch to all client contacts from the assigned Client.
    """
    assign_owners_for(batch)


def ObjectModifiedEventHandler(batch, event):
    """Actions to be done when a batch is modified. If a client has been
    assigned to the batch, this function assigns the role "Owner" for the
    batch to all client contacts from the assigned Client.
    """
    purge_owners_for(batch)


def assign_owners_for(batch):
    """Assign the role "Owner" to the contacts of the client assigned to the
    batch passed in, if any
    """
    client = batch.getClient()
    if not client:
        return False

    contacts = client.objectValues("Contact")
    users = map(lambda contact: contact.getUser(), contacts)
    users = filter(None, users)
    for user in users:
        security.grant_local_roles_for(batch, roles=["Owner"], user=user)
    batch.reindexObjectSecurity()
    return True


def purge_owners_for(batch):
    """Remove role "Owner" from all those client contacts that do not belong to
    the same Client the batch is assigned to and assigns the role "Owner" to
    the client contacts assigned to the batch
    """
    # Add role "Owner" for this batch to all contacts from this Client
    assign_owners_for(batch)

    # Unassign role "Owner" from contacts that belong to another Client
    batch_client = batch.getClient()
    batch_client_uid = batch_client and api.get_uid(batch_client) or None
    for client in api.search(dict(portal_type="Client"), "portal_catalog"):
        if api.get_uid(client) == batch_client_uid:
            continue

        client = api.get_object(client)
        contacts = client.objectValues("Contact")
        users = map(lambda contact: contact.getUser(), contacts)
        users = filter(None, users)
        for user in users:
            security.revoke_local_roles_for(batch, ["Owner"], user=user)
    batch.reindexObjectSecurity()