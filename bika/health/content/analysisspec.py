from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.health import bikaMessageFactory as _
from bika.health.widgets.analysisspecificationwidget import \
    AnalysisSpecificationWidget, AnalysisSpecificationPanicValidator
from bika.lims.config import PROJECTNAME as BIKALIMS_PROJECTNAME
from bika.lims.content.analysisspec import AnalysisSpec as BaseAnalysisSpec
from bika.lims.interfaces import IAnalysisSpec
from zope.component import adapts
from zope.interface import implements


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
                    description=srcwidget.description,
        )
        return schema


class AnalysisSpec(BaseAnalysisSpec):
    """ Inherits from bika.content.analysisspec.AnalysisSpec
    """

    def getResultsRangeDict(self):
        """ Overrides
            bika.content.analysisspec.AnalysisSpec.getResultRangeDict()
            Return a dictionary with the specification fields for each
            service. The keys of the dictionary are the keywords of each
            analysis service. Each service contains a dictionary in which
            each key is the name of the spec field:
            specs['keyword'] = {'min': value,
                                'max': value,
                                'error': value,
                                'minpanic': value,
                                'maxpanic': value }
        """
        specs = {}
        for spec in self.getResultsRange():
            keyword = spec['keyword']
            specs[keyword] = {}
            specs[keyword]['min'] = spec.get('min', '')
            specs[keyword]['max'] = spec.get('max', '')
            specs[keyword]['error'] = spec.get('error', '')
            specs[keyword]['minpanic'] = spec.get('minpanic', '')
            specs[keyword]['maxpanic'] = spec.get('maxpanic', '')
        return specs

    def getResultsRangesSorted(self):
        """ Overrides
            bika.content.analysisspec.AnalysisSpec.getPanicRangesSorted()
            Return an array of dictionaries, sorted by AS title:
             [{'category': <title of AS category>
               'service': <title of AS>,
               'id': <ID of AS>
               'uid': <UID of AS>
               'min': <min range spec value>
               'max': <max range spec value>
               'error': <error spec value>
               'minpanic': <min panic spec value>
               'maxpanic': <max panic spec value> }]
        """
        tool = getToolByName(self, REFERENCE_CATALOG)

        cats = {}
        for spec in self.getResultsRange():
            service = tool.lookupObject(spec['service'])
            service_title = service.Title()
            category_title = service.getCategoryTitle()
            if category_title not in cats:
                cats[category_title] = {}
            cat = cats[category_title]
            cat[service_title] = {'category': category_title,
                                  'service': service_title,
                                  'id': service.getId(),
                                  'uid': spec['service'],
                                  'min': spec.get('min', ''),
                                  'max': spec.get('max', ''),
                                  'error': spec.get('error', ''),
                                  'minpanic': spec.get('minpanic', ''),
                                  'maxpanic': spec.get('maxpanic', '')}
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

atapi.registerType(AnalysisSpec, BIKALIMS_PROJECTNAME)
