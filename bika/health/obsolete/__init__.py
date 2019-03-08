from bika.health import bikaMessageFactory as _
from bika.lims import deprecated
from zope.component import getAdapters
from zope.interface import Interface
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class ICustomPubPref(Interface):
    """Marker for custom Publication Preferences
    """

@deprecated("integration-1.3 artifact")
class CustomPubPrefVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = [
            (_('Email'),'email'),
            (_('PDF'), 'pdf')
        ]
        for name, item in getAdapters((context, ), ICustomPubPref):
            items.append(item)
        return SimpleVocabulary.fromItems(items)

CustomPubPrefVocabularyFactory = CustomPubPrefVocabulary()