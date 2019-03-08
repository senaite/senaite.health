# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.health.browser.batchfolder import BatchListingViewAdapter


class PatientBatchListingViewAdapter(BatchListingViewAdapter):

    def before_render(self):
        """Called before the listing renders
        """
        super(PatientBatchListingViewAdapter, self).before_render()

        # Hide patient columns
        self.listing.columns['getPatientID']['toggle'] = False
        self.listing.columns['getClientPatientID']['toggle'] = False
        self.listing.columns['Patient']['toggle'] = False
