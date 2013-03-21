from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME as BIKALIMS_PROJECTNAME
from bika.lims.content.analysis import Analysis as BaseAnalysis


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
        result = result and result or self.getResult()
        # if analysis result is not a number, then we assume in range
        try:
            result = float(str(result))
        except ValueError:
            return False, None, None

        specs = self.getAnalysisSpecs(specification)
        if specs == None:
            # No specs available, assume in range
            return False, None, None

        keyword = self.getService().getKeyword()
        spec = specs.getResultsRangeDict()
        if keyword in spec:
            spec_min = float(spec[keyword]['minpanic'])
            spec_max = float(spec[keyword]['maxpanic'])

            if spec_min <= result <= spec_max:
                return False, None, None

            if (not spec_min or spec_min <= result) \
                and (not spec_max or result <= spec_max):
                return False, None, None
            else:
                return True, False, spec[keyword]

        else:
            # Analysis without specification values. Assume in range
            return False, None, None

# overrides bika.lims.content.Analysis
atapi.registerType(Analysis, BIKALIMS_PROJECTNAME)
