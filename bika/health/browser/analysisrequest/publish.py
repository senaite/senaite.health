from bika.lims.browser.publish import doPublish
from bika.health import bikaMessageFactory as _h
from bika.lims import bikaMessageFactory as _


class AnalysisRequestPublish(doPublish):

    def get_mail_subject(self):
        subject, totline = doPublish.get_mail_subject(self)
        client = self.batch[0].aq_parent
        subject_items = client.getEmailSubject()
        if 'health.cp' in subject_items:
            cps = []
            blanks_found = False
            for ar in self.batch:
                pat = ar.Schema().getField('Patient').get(ar)
                cpid = pat and pat.getClientPatientID() or None
                if cpid:
                    cps.append(cpid)
                else:
                    blanks_found = True
            cps.sort()
            cps_line = _h('CPIDs: %s') % ', '.join(cps)
            if totline:
                totline += ' '
            totline += cps_line

            subject = _('Analysis results for %s') % totline
            if blanks_found:
                subject += (' ' + _('and others'))

        return subject, totline
