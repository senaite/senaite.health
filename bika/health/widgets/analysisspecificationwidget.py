from AccessControl import ClassSecurityInfo
from bika.health import bikaMessageFactory as _
from bika.lims.browser.widgets.analysisspecificationwidget import \
    AnalysisSpecificationView as BaseView, \
    AnalysisSpecificationWidget as BaseWidget
from Products.Archetypes.Registry import registerWidget


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
            if len(values[i]) > 0:
                uid = values[i][0]['uid']
                try:
                    float(form['minpanic'][0][uid])
                    float(form['maxpanic'][0][uid])
                except:
                    continue
                values[i][0]['minpanic'] = form['minpanic'][0][uid]
                values[i][0]['maxpanic'] = form['maxpanic'][0][uid]

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
               title = 'Analysis Specification Results',
               description = ('Analysis Specification Results'))
