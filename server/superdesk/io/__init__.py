# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


"""Superdesk IO"""
import logging
import superdesk
from superdesk.etree import etree
from superdesk.celery_app import celery


parsers = []
providers = {}
allowed_providers = []
logger = logging.getLogger(__name__)

from .commands.remove_expired_content import RemoveExpiredContent
from .commands.update_ingest import UpdateIngest
from .commands.add_provider import AddProvider  # NOQA


def init_app(app):
    from .ingest_provider_model import IngestProviderResource, IngestProviderService
    endpoint_name = 'ingest_providers'
    service = IngestProviderService(endpoint_name, backend=superdesk.get_backend())
    IngestProviderResource(endpoint_name, app=app, service=service)


def register_provider(type, provider):
    providers[type] = provider
    allowed_providers.append(type)


@celery.task(soft_time_limit=15)
def update_ingest():
    UpdateIngest().run()


@celery.task
def gc_ingest():
    RemoveExpiredContent().run()


class ParserRegistry(type):
    """Registry metaclass for parsers."""

    def __init__(cls, name, bases, attrs):
        """Register sub-classes of Parser class when defined."""
        super(ParserRegistry, cls).__init__(name, bases, attrs)
        if name != 'Parser':
            parsers.append(cls())


class Parser(metaclass=ParserRegistry):
    """Base Parser class for all types of Parsers like News ML 1.2, News ML G2, NITF, etc."""

    def parse_message(self, xml, provider):
        """Parse the ingest XML and extracts the relevant elements/attributes values from the XML."""
        raise NotImplementedError()

    def can_parse(self, xml):
        """Test if parser can parse given xml."""
        raise NotImplementedError()

    def qname(self, tag, ns=None):
        if ns is None:
            ns = self.root.tag.rsplit('}')[0].lstrip('{')
        elif ns is not None and ns == 'xml':
            ns = 'http://www.w3.org/XML/1998/namespace'

        return str(etree.QName(ns, tag))


def get_xml_parser(etree):
    """Get parser for given xml.

    :param etree: parsed xml
    """
    for parser in parsers:
        if parser.can_parse(etree):
            return parser


# must be imported for registration
import superdesk.io.nitf
import superdesk.io.newsml_2_0
import superdesk.io.newsml_1_2
import superdesk.io.wenn_parser
import superdesk.io.teletype
import superdesk.io.email
import superdesk.io.dpa
register_provider('search', None)

superdesk.privilege(name='ingest_providers', label='Ingest Channels', description='User can maintain Ingest Channels.')
