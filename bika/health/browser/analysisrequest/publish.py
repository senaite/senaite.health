from bika.lims.browser.publish import doPublish
from bika.health import bikaMessageFactory as _h
from bika.lims import bikaMessageFactory as _


class AnalysisRequestPublish(doPublish):

    def get_mail_subject(self, ar):
        subject, totline = doPublish.get_mail_subject(self, ar)
        client = ar.aq_parent
        subject_items = client.getEmailSubject()
        if 'health.cp' in subject_items:
            pat = ar.Schema().getField('Patient').get(ar)
            cpid = pat and pat.getClientPatientID() or None
            if cpid:
                cps_line = _h('CPID: %s') % cpid
                if totline:
                    totline += ' '
                totline += cps_line

            subject = _('Analysis results for %s') % totline

        return subject, totline
