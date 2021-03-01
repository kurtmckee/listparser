# This file is part of listparser.
# Copyright 2009-2021 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import html.entities
import io
from typing import Dict, Optional, Tuple, Union
import xml.sax

try:
    import requests
except ImportError:
    requests = None

from . import common
from . import foaf
from . import igoogle
from . import opml


__author__ = 'Kurt McKee <contactme@kurtmckee.org>'
__url__ = 'https://github.com/kurtmckee/listparser'
__version__ = '0.18'


def parse(
        parse_obj: Union[str, bytes],
        inject: bool = False,
) -> common.SuperDict:
    """Parse a subscription list and return a dict containing the results.

    *parse_obj* must be one of the following:

    *   a string containing a URL
    *   a string or bytes object containing an XML document

    If *inject* is True, HTML character references will be injected into
    the XML document before it is parsed.

    The dictionary returned will contain all of the parsed information,
    webserver HTTP response headers, and any exception encountered.
    """

    guarantees = {
        'bozo': False,
        'bozo_exception': None,
        'feeds': [],
        'lists': [],
        'opportunities': [],
        'meta': common.SuperDict(),
        'version': '',
    }
    content, info = get_content(parse_obj)
    guarantees.update(info)
    if not content:
        return common.SuperDict(guarantees)

    handler = Handler()
    handler.harvest.update(guarantees)
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, True)
    parser.setContentHandler(handler)
    parser.setErrorHandler(handler)
    if inject:
        content_file = Injector(content)
    else:
        content_file = io.BytesIO(content)
    parser.parse(content_file)

    # Test if a DOCTYPE injection is needed
    if handler.harvest['bozo_exception']:
        if 'entity' in handler.harvest['bozo_exception'].__str__():
            if not inject:
                return parse(content, inject=True)
    # Make it clear that the XML file is broken
    # (if no other exception has been assigned)
    if inject and not handler.harvest['bozo']:
        handler.harvest['bozo'] = True
        handler.harvest['bozo_exception'] = ListError('undefined entity found')
    return common.SuperDict(handler.harvest)


class Handler(xml.sax.handler.ContentHandler, xml.sax.handler.ErrorHandler,
              foaf.FoafMixin, igoogle.IgoogleMixin, opml.OpmlMixin):
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self.harvest = {}
        self.expect = False
        self._characters = str()
        self.hierarchy = []
        self.flag_agent = False
        self.flag_feed = False
        self.flag_new_title = False
        self.flag_opportunity = False
        self.flag_group = False
        # found_urls = {url: (append_to_key, obj)}
        self.found_urls = {}
        # group_objs = [(append_to_key, obj)]
        self.group_objs = []
        self.agent_feeds = []
        self.agent_lists = []
        self.agent_opps = []
        self.foaf_name = []

        self.start_methods = {}
        self.end_methods = {}

    def raise_bozo(self, err):
        self.harvest['bozo'] = True
        if isinstance(err, str):
            self.harvest['bozo_exception'] = ListError(err)
        else:
            self.harvest['bozo_exception'] = err

    # ErrorHandler functions
    def warning(self, exception):
        self.raise_bozo(exception)
        return
    error = warning
    fatalError = warning

    # ContentHandler functions
    def startElementNS(self, name, qname, attrs):
        try:
            method = self.start_methods[name]
        except KeyError:
            fn = ''
            if name[0] in common.namespaces:
                fn = f'_start_{common.namespaces[name[0]]}_{name[1]}'
            elif name[0] is None:
                fn = f'_start_opml_{name[1]}'
            self.start_methods[name] = method = getattr(self, fn, None)

        if method:
            method(attrs)

    def endElementNS(self, name, qname):
        try:
            method = self.end_methods[name]
        except KeyError:
            fn = ''
            if name[0] in common.namespaces:
                fn = f'_end_{common.namespaces[name[0]]}_{name[1]}'
            elif name[0] is None:
                fn = f'_end_opml_{name[1]}'
            self.end_methods[name] = method = getattr(self, fn, None)

        if method:
            method()

            # Always disable and reset character capture in order to
            # reduce code duplication in the _end_opml_* functions.
            self.expect = False
            self._characters = str()

    def characters(self, content):
        if self.expect:
            self._characters += content


def get_content(obj) -> Tuple[Optional[bytes], Dict]:
    if isinstance(obj, bytes):
        return obj, {'bozo': False, 'bozo_exception': None}
    elif not isinstance(obj, str):
        # Only str and bytes objects can be parsed.
        error = ListError('parse() called with unparsable object')
        return None, {'bozo': True, 'bozo_exception': error}
    elif not obj.startswith(('http://', 'https://')):
        # It's not a URL, so it must be treated as an XML document.
        return obj.encode('utf8'), {
            'bozo': False,
            'bozo_exception': None,
        }

    # It's a URL. Confirm requests is installed.
    elif requests is None:
        message = f"requests is not installed so {obj} cannot be retrieved"
        return None, {
            'bozo': True,
            'bozo_exception': ListError(message),
        }

    headers = {'user-agent': f'listparser/{__version__} +{__url__}'}
    try:
        response = requests.get(obj, headers=headers, timeout=30)
    except (
            requests.exceptions.RequestException,
            requests.exceptions.BaseHTTPError,
    ) as error:
        return None, {'bozo': True, 'bozo_exception': error}

    return response.text.encode('utf8'), {
        'bozo': False,
        'bozo_exception': None,
    }


class Injector:
    """
    Injector buffers read() calls to a file-like object in order to
    inject a DOCTYPE containing HTML entity definitions immediately
    following the XML declaration.
    """
    def __init__(self, content: bytes):
        self.content = io.BytesIO(content)
        self.injected = False
        self.cache = b''

    def read(self, size: int):
        # Read from the cache (and the object if necessary)
        read = self.cache[:size]
        if len(self.cache) < size:
            read += self.content.read(size - len(self.cache))
        self.cache = self.cache[size:]

        if self.injected or b'>' not in read:
            return read

        # Inject the entity declarations into the cache
        entities = ''
        for k, v in html.entities.name2codepoint.items():
            entities += '<!ENTITY {0} "&#{1};">'.format(k, v)
        # The '>' is deliberately missing; it will be appended by join()
        doctype = '<!DOCTYPE anyroot [{0}]'.format(entities)
        content = read.split(b'>', 1)
        content.insert(1, doctype.encode('utf8'))
        self.cache = b'>'.join(content)
        self.injected = True

        ret = self.cache[:size]
        self.cache = self.cache[size:]
        return ret

    def __getattr__(self, name):
        return getattr(self.content, name)


class ListError(Exception):
    """Used when a specification deviation is encountered in an XML file."""
    pass
