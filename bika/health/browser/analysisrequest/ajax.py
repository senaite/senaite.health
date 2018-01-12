# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.health import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.analysisrequest.add import AnalysisRequestSubmit as BaseClass
from bika.lims.utils import tmpID
from bika.lims.idserver import renameAfterCreation
from bika.lims.browser.analysisrequest.add import ajax_form_error
from bika.health.catalog import CATALOG_PATIENT_LISTING
from Products.CMFCore.utils import getToolByName
from bika.health import logger
from collective.taskqueue import taskqueue
from collective.taskqueue.interfaces import ITaskQueue
from zope.component import queryUtility
import transaction
import json


class AnalysisRequestSubmit(BaseClass):

    def validate_form(self):
        # Create new Anonymous Patients as needed
        uc = getToolByName(self.context, 'uid_catalog')
        cpt = getToolByName(self.context, CATALOG_PATIENT_LISTING)
        form = self.request.form
        formc = self.request.form.copy()
        state = json.loads(formc.get('state'))
        if not state:
            # BaseClass deals with state
            BaseClass.validate_form(self)
            return

        for key in state.keys():
            values = state[key].copy()
            patuid = values.get('Patient', '')
            if patuid == '' and values.get('Analyses') != []:
                msg = t(_('Required fields have no values: Patient'))
                ajax_form_error(self.errors, arnum=key, message=msg)
                continue
            elif patuid == 'anonymous':
                clientpatientid = values.get('ClientPatientID', '')
                # Check if has already been created
                proxies = cpt(getClientPatientID=clientpatientid)
                if proxies and len(proxies) > 0:
                    patient = proxies[0].getObject()
                else:
                    # Create an anonymous patient
                    client = uc(UID=values['Client'])[0].getObject()
                    _id = client.patients.invokeFactory('Patient', id=tmpID())
                    patient = client.patients[_id]
                    patient.edit(Anonymous = 1,
                                 Gender = "dk",
                                 PrimaryReferrer = client.UID(),
                                 Firstname = _("AP"),
                                 Surname = clientpatientid,
                                 ClientPatientID = clientpatientid)
                    patient.unmarkCreationFlag()
                    patient.reindexObject()
                    client.reindexObject()
                    renameAfterCreation(patient)

                values['Patient']=patient.UID()
                state[key] = values
        formc['state'] = json.JSONEncoder().encode(state)
        self.request.form = formc
        BaseClass.validate_form(self)


class AsyncAnalysisRequestSubmit(AnalysisRequestSubmit):

    def process_form(self):

        num_analyses = 0
        uids_arr = [ar.get('Analyses', []) for ar in self.valid_states.values()]
        for arr in uids_arr:
            num_analyses += len(arr)

        if num_analyses < 50:
            # Do not process Asynchronously
            return AnalysisRequestSubmit.process_form(self)

        # Only load asynchronously if queue ar-create is available
        task_queue = queryUtility(ITaskQueue, name='ar-create')
        if task_queue is None:
            # ar-create queue not registered, create synchronously
            return AnalysisRequestSubmit.process_form(self)
        else:
            # ar-create queue registered, create asynchronously
            path = self.request.PATH_INFO
            path = path.replace('_submit_async', '_submit')
            task_queue.add(path, method='POST')
            msg = _('One job added to the Analysis Request creation queue')
            self.context.plone_utils.addPortalMessage(msg, 'info')
            return json.dumps({'success': 'With taskqueue'})
