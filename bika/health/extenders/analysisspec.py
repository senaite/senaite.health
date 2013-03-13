""" http://pypi.python.org/pypi/archetypes.schemaextender
"""
from AccessControl import ClassSecurityInfo
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.health import bikaMessageFactory as _
from bika.lims.interfaces import IAnalysisSpec
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.interface import implements
from bika.health.widgets.analysisspecificationwidget import \
    AnalysisSpecificationWidget, AnalysisSpecificationPanicValidator


class AnalysisSpecSchemaExtender(object):
    adapts(IAnalysisSpec)
    implements(IOrderableSchemaExtender)
    security = ClassSecurityInfo()
    fields = []

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, schematas):
        schematas['default'] = ['id',
                                'title',
                                'description',
                                'SampleType',
                                'SampleTypeTitle',
                                'SampleTypeUID',
                                'ResultsRange',
                                'ClientUID']
        return schematas

    security.declarePublic('getPanicRangesDict')
    def getPanicRangesDict(self):
        specs = {}
        for spec in self.getResultsRange():
            keyword = spec['keyword']
            specs[keyword] = {}
            specs[keyword]['minpanic'] = spec['minpanic']
            specs[keyword]['maxpanic'] = spec['maxpanic']
        return specs

    security.declarePublic('getResultsRangesSorted')
    def getPanicRangesSorted(self):
        tool = getToolByName(self, REFERENCE_CATALOG)

        cats = {}
        for spec in self.getResultsRange():
            service = tool.lookupObject(spec['service'])
            service_title = service.Title()
            category_title = service.getCategoryTitle()
            if category_title not in cats.keys():
                cats[category_title] = {}
            cat = cats[category_title]
            cat[service_title] = {'category': category_title,
                                  'service': service_title,
                                  'id': service.getId(),
                                  'uid': spec['service'],
                                  'minpanic': spec['minpanic'],
                                  'maxpanic': spec['maxpanic']}
        cat_keys = cats.keys()
        cat_keys.sort(lambda x, y: cmp(x.lower(), y.lower()))
        sorted_specs = []
        for cat in cat_keys:
            services = cats[cat]
            service_keys = services.keys()
            service_keys.sort(lambda x, y: cmp(x.lower(), y.lower()))
            for service_key in service_keys:
                sorted_specs.append(services[service_key])

        return sorted_specs


class AnalysisSpecSchemaModifier(object):
    adapts(IAnalysisSpec)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):

        # Add panic alert range columns
        validator = AnalysisSpecificationPanicValidator()
        schema['ResultsRange'].subfields += ('minpanic', 'maxpanic')
        schema['ResultsRange'].subfield_validators['minpanic'] = validator
        schema['ResultsRange'].subfield_validators['maxpanic'] = validator
        schema['ResultsRange'].subfield_labels['minpanic'] = _('Min panic')
        schema['ResultsRange'].subfield_labels['maxpanic'] = _('Max panic')
        srcwidget = schema['ResultsRange'].widget
        schema['ResultsRange'].widget = AnalysisSpecificationWidget(
                    checkbox_bound=srcwidget.checkbox_bound,
                    label=srcwidget.label,
                    description=srcwidget.description + _(
                " Set panic min and max levels to indicate a result that "
                "could indicate life threats. Any result outside this panic "
                "range will raise an alert and an email will be sent "
                "automatically to the lab manager/s to consider a re-test to "
                "confirm the panic value. The lab manager may choose "
                "immediately alert the client or do a re-test first."),
        )
        return schema
