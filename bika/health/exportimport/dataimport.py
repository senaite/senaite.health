from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.content.instrument import getDataInterfaces
from bika.lims.exportimport import instruments
from bika.lims.exportimport.dataimport import ImportView as BaseView
from bika.health.exportimport.load_setup_data import LoadSetupData
from operator import itemgetter
from pkg_resources import *
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import plone


class ImportView(BaseView):

    def __call__(self):
        if 'submitted' in self.request:
            if 'setupfile' in self.request.form or \
               'setupexisting' in self.request.form:
                lsd = LoadSetupData(self.context, self.request)
                return lsd()
            else:
                exim = getattr(instruments, self.request['exim'])
                return exim.Import(self.context, self.request)
        else:
            return BaseView.__call__(self)
