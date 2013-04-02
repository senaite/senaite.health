from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME as BIKALIMS_PROJECTNAME
from bika.lims.content.analysis import Analysis as BaseAnalysis
from archetypes.schemaextender.interfaces import ISchemaExtender
from bika.lims.interfaces import IAnalysis
from zope.component import adapts
from zope.interface import implements


class AnalysisSchemaExtender(object):
    adapts(IAnalysis)
    implements(ISchemaExtender)

    fields = []

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


class Analysis(BaseAnalysis):
    """ Inherits from bika.lims.content.Analysis
    """

    def isInPanicRange(self, result=None, specification=None):
        """ Check if result value is 'in panic'.
            If result is None, analysis.getResult() is called for the result.
            If specification is None, super.getAnalysisSpecs() is called
            Return True, False, spec if in panic range
            Return False, None, None if the result is in safe range
        """
        result = result is not None and str(result) or self.getResult()
        # if analysis result is not a number, then we assume in range
        try:
            result = float(str(result))
        except ValueError:
            return False, None, None

        specs = self.getAnalysisSpecs(specification)
        spec_min = None
        spec_max = None
        if specs == None:
            # No specs available, assume in range
            return False, None, None

        keyword = self.getService().getKeyword()
        spec = specs.getResultsRangeDict()
        if keyword in spec:
            try:
                spec_min = float(spec[keyword]['minpanic'])
            except:
                spec_min = None
                pass

            try:
                spec_max = float(spec[keyword]['maxpanic'])
            except:
                spec_max = None
                pass

            if (not spec_min and not spec_max):
                # No min and max values defined
                return False, None, None

            elif spec_min and spec_max \
                and spec_min <= result <= spec_max:
                # min and max values defined
                return False, None, None

            elif spec_min and not spec_max and spec_min <= result:
                # max value not defined
                return False, None, None

            elif not spec_min and spec_max and spec_max >= result:
                # min value not defined
                return False, None, None

            else:
                return True, False, spec[keyword]

        else:
            # Analysis without specification values. Assume in range
            return False, None, None

# overrides bika.lims.content.Analysis
atapi.registerType(Analysis, BIKALIMS_PROJECTNAME)
