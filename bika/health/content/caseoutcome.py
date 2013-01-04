from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import registerType
from bika.lims.content.bikaschema import BikaSchema
from bika.health.config import PROJECTNAME

schema = BikaSchema.copy()
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class CaseOutcome(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(CaseOutcome, PROJECTNAME)
