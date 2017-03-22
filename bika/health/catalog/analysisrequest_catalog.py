# This file is part of Bika Health
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING

# Defines the extension for catalogs created in Bika LIMS.
# Only add the items you would like to add!
analysisrequest_catalog_definition = {
    CATALOG_ANALYSIS_REQUEST_LISTING: {
            'indexes': {
                'getDoctorUID': 'FieldIndex',
                'getPatientUID': 'FieldIndex',
                # To sort columns
                'getPatient': 'FieldIndex',
            },
            'columns': [
                'getDoctorUID',
                'getPatientUID',
            ]
        }
    }
