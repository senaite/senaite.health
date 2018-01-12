# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from bika.lims.browser.multifile import MultifileView


class PatientMultifileView(MultifileView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(PatientMultifileView, self).__init__(context, request)
        self.title = self.context.translate(_("Patient Attachments"))
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=Multifile',
                                 'icon': '++resource++bika.lims.images/add.png'}}
