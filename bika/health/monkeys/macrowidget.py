# TODO Remove for compatibility with senaite.core v1.3.3
# Superseded by https://github.com/senaite/senaite.core/pull/1466

from AccessControl.unauthorized import Unauthorized


def __call__(self, mode, instance, context=None):
    self.bootstrap(instance)
    # If an attribute called macro_<mode> exists resolve that
    # before the generic macro, this lets other projects
    # create more partial widgets
    macro = getattr(self, 'macro_%s' % mode, self.macro)
    if macro == "bika_widgets/referencewidget":
        macro = "bika_health_widgets/referencewidget"

    # Now split the macro into optional parts using '|'
    # if the first part doesn't exist, the search continues
    paths = macro.split('|')
    if len(paths) == 1 and macro == self.macro:
        # Prepend the default (optional) customization element
        paths.insert(0, 'at_widget_%s' % self.macro.split('/')[-1])
    for path in paths:
        try:
            template = instance.restrictedTraverse(path=path)
            if template:
                return template.macros[mode]
        except (Unauthorized, AttributeError, KeyError):
            # This means we didn't have access or it doesn't exist
            pass
    raise AttributeError("Macro %s does not exist for %s" % (macro,
                                                             instance))