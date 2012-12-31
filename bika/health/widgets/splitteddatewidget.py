from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from Products.CMFPlone.i18nl10n import ulocalized_time


class SplittedDateWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'ulocalized_time': ulocalized_time,
        'macro': "bika_health_widgets/splitteddatewidget",
        'helper_js': ("bika_health_widgets/splitteddatewidget.js",),
        'helper_css': ("bika_health_widgets/splitteddatewidget.css",),
        'changeYear': True,
        'changeMonth': True,
        'changeDay': True,
        'maxDate': '+0d',
        'yearRange': '-100:+0'
    })
    security = ClassSecurityInfo()

registerWidget(SplittedDateWidget,
               title='SplittedDateWidget',
               description=('Simple control with three input fields (year, month, day)'),
               )
