from bika.health import bikaMessageFactory as _
from bika.lims.browser.calcs import ajaxCalculateAnalysisEntry as BaseClass
from bika.lims import logger


class ajaxCalculateAnalysisEntry(BaseClass):

    def calculate(self, uid=None):
        super(ajaxCalculateAnalysisEntry, self).calculate(uid)
        # Check if results are outside from panic level range
        analysis = self.analyses[uid]
        aresults = [item for item in self.results if item['uid'] == uid]
        for aresult in aresults:
            inpanic = [False, None, None]
            try:
                inpanic = analysis.isInPanicRange(aresult['result'], self.spec)
            except:
                logger.warning("Call error: isInPanicRange for analysis %s" % uid)
                pass

            if inpanic[0] == True:
                range_str = _("minpanic") + " " + \
                            str(inpanic[2]['minpanic']) + ", " + \
                            _("maxpanic") + " " + \
                            str(inpanic[2]['maxpanic'])

                # Check if already an alert for this result
                msg = _("Result exceeded panic levels") + " (%s)" % range_str
                alert = {'uid': uid,
                         'field': 'Result',
                         'icon': 'lifethreat',
                         'product': 'bika.health',
                         'msg': msg}

                aalerts = [alert for alert in self.alerts \
                           if alert['uid'] == uid]
                if len(aalerts) > 0:
                    self.alerts.remove(aalerts[0])
                self.alerts.append(alert)
