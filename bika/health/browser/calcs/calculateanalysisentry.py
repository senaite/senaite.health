from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.lims.browser.calcs import ajaxCalculateAnalysisEntry as BaseClass


class ajaxCalculateAnalysisEntry(BaseClass):

    def calculate(self, uid=None):
        super(ajaxCalculateAnalysisEntry, self).calculate(uid)

        # Check if results are outside from panic level range
        analysis = self.analyses[uid]
        aresults = [item for item in self.results if item['uid'] == uid]
        for aresult in aresults:
            inpanic = self.result_in_panic(analysis,
                                           aresult['result'],
                                           self.spec)

            if inpanic[0] == True:
                range_str = _("minpanic") + " " + \
                            str(inpanic[1]['minpanic']) + ", " + \
                            _("maxpanic") + " " + \
                            str(inpanic[1]['maxpanic'])

                # Check if already an alert for this result
                msg = _("Result exceeds panic levels") + " (%s)" % range_str
                alert = {'uid': uid,
                         'field': 'Result',
                         'icon': 'exclamation2',
                         'msg': msg}

                aalerts = [alert for alert in self.alerts \
                           if alert['uid'] == uid]
                if len(aalerts) > 0:
                    alert = aalerts[0]
                    alert['msg'] = alert['msg'] + ". %s" % msg
                    self.alerts.remove(aalerts[0])
                self.alerts.append(alert)

    def result_in_panic(self, analysis, result=None, specification="lab"):
        """ Check if result value is 'in panic'.
            If result is None, analysis.getResult() is called for the result.
            Return True,failed_spec if in panic range
            Return False, None if the result is in safe range
        """
        client_uid = specification == "client" and analysis.getClientUID() or \
            analysis.bika_setup.bika_analysisspecs.UID()

        result = result and result or analysis.getResult()

        # if analysis result is not a number, assume in safe range
        try:
            result = float(str(result))
        except ValueError:
            return False, None

        service = analysis.getService()
        keyword = service.getKeyword()
        sampletype = analysis.aq_parent.getSample().getSampleType()
        sampletype_uid = sampletype and sampletype.UID() or ''
        bsc = getToolByName(self, 'bika_setup_catalog')
        proxies = bsc(portal_type='AnalysisSpec',
                      getSampleTypeUID=sampletype_uid)
        a = [p for p in proxies if p.getClientUID == client_uid]
        if a:
            spec_obj = a[0].getObject()
            # Get spec panic ranges
            spec = {}
            for specs in spec_obj.getResultsRange():
                key = specs['keyword']
                spec[key] = {}
                spec[key]['minpanic'] = specs['minpanic']
                spec[key]['maxpanic'] = specs['maxpanic']
        else:
            # if no range is specified we assume it is in range
            return False, None

        if keyword in spec:
            spec_minpanic = None
            spec_maxpanic = None
            if 'minpanic' in spec[keyword]:
                spec_minpanic = float(spec[keyword]['minpanic'])
            if 'maxpanic' in spec[keyword]:
                spec_maxpanic = float(spec[keyword]['maxpanic'])

            if (not spec_minpanic or spec_minpanic <= result) \
                and (not spec_maxpanic or result <= spec_maxpanic):
                return False, None
            else:
                return True, spec[keyword]
        else:
            return False, None
