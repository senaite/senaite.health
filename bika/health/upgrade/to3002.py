from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    # Add patient action for client portal_type programmatically
    portal = aq_parent(aq_inner(tool))
    client = portal.portal_types.getTypeInfo("Client")
    client.addAction(id="patients",
        name="Patients",
        action="string:${object_url}/patients",
        permission="BIKA: Edit Patient",
        category="object",
        visible=True,
        icon_expr="string:${portal_url}/images/patient.png",
        link_target="",
        description="",
        condition="")

    return True
