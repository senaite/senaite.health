from bika.lims import workflow as wf
from bika.lims import api
from bika.lims.api import security


def ObjectInitializedEventHandler(patient, event):
    """Actions to be done when a patient is created. If a client has been
    assigned to the patient, this function assigns the role "Owner" for the
    patient to all client contacts from the assigned Client.
    """
    assign_owners_for(patient)


def ObjectModifiedEventHandler(patient, event):
    """Actions to be done when a patient is modified. If a client has been
    assigned to the patient, this function assigns the role "Owner" for the
    patient to all client contacts from the assigned Client.
    """
    purge_owners_for(patient)


def assign_owners_for(patient):
    """Assign the role "Owner" to the contacts of the client assigned to the
    patient passed in, if any
    """
    client = patient.getClient()
    if not client:
        return False

    contacts = client.objectValues("Contact")
    users = map(lambda contact: contact.getUser(), contacts)
    users = filter(None, users)
    for user in users:
        security.grant_local_roles_for(patient, roles=["Owner"], user=user)
    patient.reindexObjectSecurity()
    return True


def purge_owners_for(patient):
    """Remove role "Owner" from all those client contacts that do not belong to
    the same Client the patient is assigned to and assigns the role "Owner" to
    the client contacts assigned to the patient
    """
    # Add role "Owner" for this Patient to all contacts from this Client
    assign_owners_for(patient)

    # Unassign role "Owner" from contacts that belong to another Client
    patient_client = patient.getClient()
    patient_client_uid = patient_client and api.get_uid(patient_client) or None
    for client in api.search(dict(portal_type="Client"), "portal_catalog"):
        if api.get_uid(client) == patient_client_uid:
            continue

        client = api.get_object(client)
        contacts = client.objectValues("Contact")
        users = map(lambda contact: contact.getUser(), contacts)
        users = filter(None, users)
        for user in users:
            security.revoke_local_roles_for(patient, ["Owner"], user=user)
    patient.reindexObjectSecurity()