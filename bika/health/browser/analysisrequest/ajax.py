from bika.health import bikaMessageFactory as _
from bika.lims.browser.analysisrequest.add import ajaxAnalysisRequestSubmit as BaseClass
from bika.lims.utils import tmpID
from bika.lims.idserver import renameAfterCreation
from Products.CMFCore.utils import getToolByName


class AnalysisRequestSubmit(BaseClass):

    def __call__(self):

        # Create new Anonymous Patients as needed
        uc = getToolByName(self.context, 'uid_catalog')
        bpc = getToolByName(self.context, 'bika_patient_catalog')
        form = self.request.form
        formc = self.request.form.copy()
        for column in range(int(form['col_count'])):
            arkey = "ar.%s" % column
            values = form[arkey].copy()
            patuid = values.get('Patient_uid', '')
            if patuid == 'anonymous':
                clientpatientid = values.get('ClientPatientID', '')
                # Check if has already been created
                proxies = bpc(getClientPatientID=clientpatientid)
                if proxies and len(proxies) > 0:
                    patient = proxies[0].getObject()
                else:
                    # Create an anonymous patient
                    client = uc(UID=values['Client_uid'])[0].getObject()
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

                values['Patient_uid']=patient.UID()
                values['Patient']=patient.Title()
                formc[arkey] = values

        self.request.form = formc
        return BaseClass.__call__(self)
