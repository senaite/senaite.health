# -*- coding: utf-8 -*-

from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME as BIKALIMS_PROJECTNAME
from bika.lims.content.analysisspec import AnalysisSpec as BaseAnalysisSpec


class AnalysisSpec(BaseAnalysisSpec):
    """ Inherits from bika.content.analysisspec.AnalysisSpec
    """


atapi.registerType(AnalysisSpec, BIKALIMS_PROJECTNAME)
