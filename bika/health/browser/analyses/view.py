from bika.lims import logger
from bika.lims.browser.analyses import AnalysesView as BaseView
from bika.health import bikaMessageFactory as _


class AnalysesView(BaseView):

    def getOutOfRangeAlerts(self):
        """ Overrides
            bika.lims.browser.analyses.AnalysesView.getOutOfRangeAlerts()
            Takes into account panic alerts when submitted results exceed panic
            levels.
        """
        alerts = super(AnalysesView, self).getOutOfRangeAlerts()
        for item in self.items:
            obj = item['obj']
            inpanic = False
            try:
                inpanic, acceptable, spec = obj.isInPanicRange()
            except:
                logger.warning("Call error: isInPanicRange for analysis %s" % obj.UID())
                pass

            if inpanic:
                rngstr = _("minpanic") + " " + str(spec['minpanic']) + \
                         ", " + \
                         _("maxpanic") + " " + str(spec['maxpanic'])

                if acceptable:
                    message = _('Result in shoulder panic range') \
                            + " (%s)" % rngstr
                else:
                    message = _('Result exceeded panic level') \
                            + ' (%s)' % rngstr

                alerts[obj.UID()] = {'result': obj.getResult(),
                                     'icon': 'lifethreat',
                                     'product': 'bika.health',
                                     'msg': message}
        return alerts
