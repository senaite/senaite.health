from bika.lims.config import *
from Products.Archetypes.public import DisplayList
from bika.lims import bikaMessageFactory as _b
from bika.health import bikaMessageFactory as _
from bika.health.permissions import *

PROJECTNAME = "bika.health"

ETHNICITIES = DisplayList((
    ('Native American', _('Native American')),
    ('Asian', _('Asian')),
    ('Black', _('Black')),
    ('Native Hawaiian or Other Pacific Islander', _('Native Hawaiian or Other Pacific Islander')),
    ('White', _('White')),
    ('Hispanic or Latino', _('Hispanic or Latino')),
))

GENDERS = DisplayList((
    ('male', _('Male')),
    ('female', _('Female')),
    ('dk', _("Don't Know")),
    ))

GENDERS_APPLY = DisplayList((
    ('male', _('Male')),
    ('female', _('Female')),
    ('dk', _("Both")),
))

MENSTRUAL_STATUSES = DisplayList((
    ('regular', _('Regular')),
    ('irregular', _('Irregular')),
    ('none', _('No menstrual cycle')),
))

EMAIL_SUBJECT_OPTIONS.add('health.cp', _('Client PID'))
