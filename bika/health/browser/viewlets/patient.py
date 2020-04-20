from bika.health.utils import is_internal_client
from plone.app.layout.viewlets import ViewletBase
from bika.lims import api


class PatientSharedViewlet(ViewletBase):
    """Display a message stating whether the Patient is shared among Internal
    Clients or rather is a private patient from a Client
    """

    def is_visible(self):
        """Returns whether the viewlet must be visible or not
        """
        if self.context.isTemporary():
            # Temporary object, not yet created
            return False

        logged_client = api.get_current_client()
        if not logged_client:
            # Current user is from Lab, display always
            return True

        # Only display the viewlet if the current user does belong to an
        # Internal Client. It does not make sense to display this viewlet if
        # the user is from an external client, cause in such case, he/she will
        # only be able to see the its own patients
        return is_internal_client(logged_client)

    def is_shared_patient(self):
        """Returns whether the current Patient is shared among Internal Clients
        """
        client = self.context.getClient()
        return not client or is_internal_client(client)

    def get_client_name(self):
        """Returns the client name the patient is assigned to
        """
        client = self.context.getClient()
        return client and api.get_title(self.context.getClient()) or ""
