from AccessControl import ClassSecurityInfo
from bika.health import bikaMessageFactory as _
from bika.lims.browser.widgets.analysisspecificationwidget import \
    AnalysisSpecificationView as BaseView, \
    AnalysisSpecificationWidget as BaseWidget
from Products.Archetypes.Registry import registerWidget
from Products.CMFCore.utils import getToolByName
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation
from zope.interface import implements


class AnalysisSpecificationView(BaseView):

    def __init__(self, context, request, fieldvalue, allow_edit):
        BaseView.__init__(self, context, request, fieldvalue, allow_edit)

        self.columns['minpanic'] = {'title': _('Min panic'), 'sortable': False}
        self.columns['maxpanic'] = {'title': _('Max panic'), 'sortable': False}
        self.review_states[0]['columns'] += ['minpanic', 'maxpanic']

    def folderitems(self):
        items = BaseView.folderitems(self)
        for i in range(len(items)):
            keyword = items[i]['keyword']
            if keyword in self.specsresults:
                res = self.specsresults[keyword]
                items[i]['minpanic'] = res.get('minpanic', '')
                items[i]['maxpanic'] = res.get('maxpanic', '')
            else:
                items[i]['minpanic'] = ''
                items[i]['maxpanic'] = ''
            items[i]['allow_edit'] += ['minpanic', 'maxpanic']
        return items


class AnalysisSpecificationWidget(BaseWidget):
    _properties = BaseWidget._properties.copy()

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, 
                     empty_marker=None, emptyReturnsMarker=False):
        values = BaseWidget.process_form(self, instance, field, form,
                                         empty_marker, emptyReturnsMarker)
        for i in range(len(values)):
            for j in range(len(values[i])):
                uid = values[i][j]['uid']
                uid = values[i][j]['uid']
                try:
                    float(form['minpanic'][0][uid])
                    float(form['maxpanic'][0][uid])
                except:
                    continue
                values[i][j]['minpanic'] = form['minpanic'][0][uid]
                values[i][j]['maxpanic'] = form['maxpanic'][0][uid]

        return values

    security.declarePublic('AnalysisSpecificationResults')
    def AnalysisSpecificationResults(self, field, allow_edit=False):
        fieldvalue = getattr(field, field.accessor)()
        view = AnalysisSpecificationView(self,
                                            self.REQUEST,
                                            fieldvalue=fieldvalue,
                                            allow_edit=allow_edit)
        return view.contents_table(table_only=True)

registerWidget(AnalysisSpecificationWidget,
               title='Analysis Specification Results',
               description=('Analysis Specification Results'))


class AnalysisSpecificationPanicValidator:
    implements(IValidator)
    name = "analysisspecs_panic_validator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        ts = getToolByName(instance, 'translation_service').translate

        if instance.REQUEST.get('validated', '') == self.name:
            return True
        else:
            instance.REQUEST['validated'] = self.name

        pmins = instance.REQUEST.get('minpanic', {})[0]
        pmaxs = instance.REQUEST.get('maxpanic', {})[0]
        uids = pmins.keys()
        for uid in uids:
            pmin = pmins.get(uid, '') == '' and '0' or pmins[uid]
            pmax = pmaxs.get(uid, '') == '' and '0' or pmaxs[uid]

            # Values must be numbers
            try:
                pmin = float(pmin)
            except:
                return ts(_("Validation failed: Panic min value must be "
                            "numeric"))

            try:
                pmax = float(pmax)
            except:
                return ts(_("Validation failed: Panic min value must be "
                            "numeric"))

            if pmin > pmax:
                return ts(_("Validation failed: Panic max value must be "
                            "greater than panic min value"))
        return True

validation.register(AnalysisSpecificationPanicValidator())
