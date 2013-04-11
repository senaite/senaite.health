""" http://pypi.python.org/pypi/archetypes.schemaextender
"""
from Products.Archetypes.public import *
from bika.lims.fields import *
from bika.lims.interfaces import IClient
from bika.health.widgets import *
from plone.indexer.decorator import indexer

@indexer(IClient)
def getClientID(instance):
    return instance.Schema()['ClientID'].get(instance)
