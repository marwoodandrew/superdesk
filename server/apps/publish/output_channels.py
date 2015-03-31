# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk import get_resource_service
from eve.utils import ParsedRequest
from superdesk.errors import SuperdeskApiError

logger = logging.getLogger(__name__)


class OutputChannelsResource(Resource):
    schema = {
        'name': {
            'type': 'string',
            'iunique': True,
            'required': True,
        },
        'description': {
            'type': 'string'
        }
    }

    datasource = {'default_sort': [('_created', -1)]}
    privileges = {'POST': 'output_channels', 'DELETE': 'output_channels', 'PATCH': 'output_channels'}


class OutputChannelsService(BaseService):
    def on_delete(self, doc):
        parsed_request = ParsedRequest()
        parsed_request.args = {'output_channels.channels': doc.get('_id')}
        if list(get_resource_service('destination_groups').find(req=parsed_request, lookup=None)).count() > 0:
            raise SuperdeskApiError.preconditionFailedError(
                message='Output Channel is associated with Destination Groups.',
                payload={'destination_groups': 1})
