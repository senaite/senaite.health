# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH.
#
# SENAITE.HEALTH is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.health.ajax.ajaxhandler import AjaxHandler


class BikaSetupAjaxHandler(AjaxHandler):

    def getDefaultPatientPublicationSettings(self, params):
        """ Returns the settings for the publication of results to patients.
            The first output param is a dictionary with the following
            key/values:
            - AllowResultsDistributionToPatients: true/false
            - PatientPublicationPreferences: array of strings (email, etc.)
            - PatientPublicationAttachmentsPermitted: true/false
            The first output param is Null if there was an error.
            The second output param is an error message if there was an error
            invoking the method. Null if there was no error.
        """
        ALLOW = 'AllowResultsDistributionToPatients'
        PREF = 'PatientPublicationPreferences'
        ATTACH = 'PatientPublicationAttachmentsPermitted'

        bs = self.context.bika_setup
        sch = bs.Schema()
        res = {ALLOW: sch[ALLOW].get(bs),
                PREF: sch[PREF].get(bs),
                ATTACH: sch[ATTACH].get(bs)}

        return res, None
