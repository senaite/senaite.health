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

from bika.lims.browser import BrowserView
from bika.lims import bikaMessageFactory as _
import plone
import sys
import json


class AjaxHandler(BrowserView):
    """ Handler for standarized ajax calls to bika.health
    """

    def __call__(self):
        """ Method invocation:
            A remote method is invoked by sending a request to a remote service.
            The request must be a single object serialized using JSON.
            It has three properties:
            - service: A String containing the name of the method to be invoked.
            - params: A dict of objects to pass as arguments to the method.
            - id: The request id. This can be of any type. It is used to match
                  the response with the request that it is replying to.
            Response:
            When the method invocation completes, the service replies with a
            response. The response is a single object serialized using JSON.
            It has three properties:
            - result: The Object returned by the invoked method. Null in case
                      there was an error invoking the method.
            - error: An Error object if there was an error invoking the method.
                     Null if there was no error.
            - id: The same id as the request it is responding to.
        """
        plone.protect.CheckAuthenticator(self.request)
        method = self.request.get('service', '')
        callid = self.request.get('id')
        params = self.request.get('params', '{}')
        params = json.loads(params)

        error = None
        result = None
        if not callid:
            error = _("No request id defined")

        if not method:
            error = _("Service not defined")
        else:
            if not hasattr(self, method):
                error = _("Service '%s' not found for %s") \
                        % (method, self.__class__.__name__)
            else:
                try:
                    # Call method
                    result, error = getattr(self, method)(params)
                except:
                    exc_value = sys.exc_info()[1]
                    error = _("Failed ajax call: %s") % exc_value
                    result = None

        response = {'result': result, 'error': error, 'id': callid}
        return json.dumps(response)
