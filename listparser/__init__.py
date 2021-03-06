# listparser - Parse OPML, FOAF, and iGoogle subscription lists.
# Copyright 2009-2017 Kurt McKee <contactme@kurtmckee.org>
#
# This file is part of listparser.
#
# listparser is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# listparser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with listparser.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import io
import sys
import xml.sax

import six
import six.moves.html_entities as html_entities
import six.moves.http_client as http_client
import six.moves.urllib as urllib

# Account for differences between the CPythons and Jython
# HACK: platform.python_implementation() might be ideal here, but
# Jython 2.5.1 doesn't have it yet, and neither do CPythons < 2.6
try:  # pragma: no cover
    # Jython
    from org.xml.sax import SAXParseException
    from com.sun.org.apache.xerces.internal.impl.io import \
        MalformedByteSequenceException
except ImportError:
    # CPython and PyPy
    SAXParseException = xml.sax.SAXParseException
    MalformedByteSequenceException = IOError

from . import common
from . import dates
from . import foaf
from . import igoogle
from . import opml


__author__ = 'Kurt McKee <contactme@kurtmckee.org>'
__url__ = 'https://github.com/kurtmckee/listparser'
__version__ = '0.18'


USER_AGENT = 'listparser/{0} +{1}'.format(__version__, __url__)


def b(text):
    """Encode unicode and string objects to bytes objects."""

    # Force `text` to the type expected by different interpreters
    # Python 3 expects type(bytes)
    # Python 2 expects type(basestring)
    if isinstance(text, six.text_type):
        return text.encode('utf8')
    return text


def parse(parse_obj, agent=None, etag=None, modified=None, inject=False):
    """Parse a subscription list and return a dict containing the results.

    :param parse_obj: A file-like object or a string containing a URL, an
        absolute or relative filename, or an XML document.
    :type parse_obj: str or file
    :param agent: User-Agent header to be sent when requesting a URL
    :type agent: str
    :param etag: The ETag header to be sent when requesting a URL.
    :type etag: str
    :param modified: The Last-Modified header to be sent when requesting a URL.
    :type modified: str or datetime.datetime

    :returns: All of the parsed information, webserver HTTP response
        headers, and any exception encountered.
    :rtype: dict

    :py:func:`~listparser.parse` is the only public function exposed by
    listparser.

    If *parse_obj* is a URL, the *agent* will identify the software
    making the request, *etag* will identify the last HTTP ETag
    header returned by the webserver, and *modified* will
    identify the last HTTP Last-Modified header returned by the
    webserver. *agent* and *etag* must be strings,
    while *modified* can be either a string or a Python
    *datetime.datetime* object.

    If *agent* is not provided, the :py:data:`~listparser.USER_AGENT` global
    variable will be used by default.
    """

    guarantees = common.SuperDict({
        'bozo': 0,
        'feeds': [],
        'lists': [],
        'opportunities': [],
        'meta': common.SuperDict(),
        'version': '',
    })
    fileobj, info = _mkfile(parse_obj, (agent or USER_AGENT), etag, modified)
    guarantees.update(info)
    if not fileobj:
        return guarantees

    handler = Handler()
    handler.harvest.update(guarantees)
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, True)
    parser.setContentHandler(handler)
    parser.setErrorHandler(handler)
    if inject:
        fileobj = Injector(fileobj)
    try:
        parser.parse(fileobj)
    except (SAXParseException, MalformedByteSequenceException):  # noqa: E501  # pragma: no cover
        # Jython propagates exceptions past the ErrorHandler.
        err = sys.exc_info()[1]
        handler.harvest.bozo = 1
        handler.harvest.bozo_exception = err
    finally:
        fileobj.close()

    # Test if a DOCTYPE injection is needed
    if hasattr(handler.harvest, 'bozo_exception'):
        if 'entity' in handler.harvest.bozo_exception.__str__():
            if not inject:
                return parse(parse_obj, agent, etag, modified, True)
    # Make it clear that the XML file is broken
    # (if no other exception has been assigned)
    if inject and not handler.harvest.bozo:
        handler.harvest.bozo = 1
        handler.harvest.bozo_exception = ListError('undefined entity found')
    return handler.harvest


class Handler(xml.sax.handler.ContentHandler, xml.sax.handler.ErrorHandler,
              foaf.FoafMixin, igoogle.IgoogleMixin, opml.OpmlMixin):
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self.harvest = common.SuperDict()
        self.expect = False
        self._characters = str()
        self.hierarchy = []
        self.flag_agent = False
        self.flag_feed = False
        self.flag_new_title = False
        self.flag_opportunity = False
        self.flag_group = False
        # found_urls = {url: (append_to_key, obj)}
        self.found_urls = common.SuperDict()
        # group_objs = [(append_to_key, obj)]
        self.group_objs = []
        self.agent_feeds = []
        self.agent_lists = []
        self.agent_opps = []
        self.foaf_name = []

    def raise_bozo(self, err):
        self.harvest.bozo = 1
        if isinstance(err, str):
            self.harvest.bozo_exception = ListError(err)
        else:
            self.harvest.bozo_exception = err

    # ErrorHandler functions
    def warning(self, exception):
        self.raise_bozo(exception)
        return
    error = warning
    fatalError = warning

    # ContentHandler functions
    def startElementNS(self, name, qname, attrs):
        fn = ''
        if name[0] in common.namespaces:
            fn = '_start_{0}_{1}'.format(common.namespaces[name[0]], name[1])
        elif name[0] is None:
            fn = '_start_opml_{0}'.format(name[1])
        if hasattr(getattr(self, fn, None), '__call__'):
            getattr(self, fn)(attrs)

    def endElementNS(self, name, qname):
        fn = ''
        if name[0] in common.namespaces:
            fn = '_end_{0}_{1}'.format(common.namespaces[name[0]], name[1])
        elif name[0] is None:
            fn = '_end_opml_{0}'.format(name[1])
        if hasattr(getattr(self, fn, None), '__call__'):
            getattr(self, fn)()
            # Always disable and reset character capture in order to
            # reduce code duplication in the _end_opml_* functions
            self.expect = False
            self._characters = str()

    def normchars(self):
        # Jython parsers split characters() calls between the bytes of
        # multibyte characters. Thus, decoding has to be put off until
        # all of the bytes are collected and the text node has ended.
        return self._characters.encode('utf8').decode('utf8').strip()

    def characters(self, content):
        if self.expect:
            self._characters += content


class HTTPRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, hdrs):
        result = urllib.request.HTTPRedirectHandler.http_error_301(
            self, req, fp, code, msg, hdrs
        )
        result.status = code
        result.newurl = result.geturl()
        return result
    # The default implementations in urllib2.HTTPRedirectHandler
    # are identical, so hardcoding a http_error_301 call above
    # won't affect anything
    http_error_302 = http_error_303 = http_error_307 = http_error_301


class HTTPErrorHandler(urllib.request.HTTPDefaultErrorHandler):
    def http_error_default(self, req, fp, code, msg, hdrs):
        # The default implementation just raises HTTPError.
        # Forget that.
        fp.status = code
        return fp


def _mkfile(obj, agent, etag, modified):
    if hasattr(obj, 'read') and hasattr(obj, 'close'):
        # It's file-like
        return obj, common.SuperDict()
    elif not isinstance(obj, (six.text_type, six.binary_type)):
        # This isn't a known-parsable object
        err = ListError('parse() called with unparsable object')
        return None, common.SuperDict({'bozo': 1, 'bozo_exception': err})
    elif not (obj.startswith('http://') or obj.startswith('https://') or
              obj.startswith('ftp://') or obj.startswith('file://')):
        # It's not a URL; test if it's an XML document
        if obj.lstrip().startswith('<'):
            return io.BytesIO(b(obj)), common.SuperDict()
        # Try dealing with it as a file
        try:
            return open(obj, 'rb'), common.SuperDict()
        except IOError:
            err = sys.exc_info()[1]
            return None, common.SuperDict({'bozo': 1, 'bozo_exception': err})
    # It's a URL
    headers = {}
    if isinstance(agent, six.string_types):
        headers['User-Agent'] = agent
    if isinstance(etag, (str, six.string_types)):
        headers['If-None-Match'] = etag
    if isinstance(modified, six.string_types):
        headers['If-Modified-Since'] = modified
    elif isinstance(modified, datetime.datetime):
        # It is assumed that `modified` is in UTC time
        headers['If-Modified-Since'] = dates._to_rfc822(modified)
    request = urllib.request.Request(obj, headers=headers)
    opener = urllib.request.build_opener(HTTPRedirectHandler, HTTPErrorHandler)
    try:
        ret = opener.open(request)
    except (urllib.error.URLError, http_client.HTTPException):
        err = sys.exc_info()[1]
        return None, common.SuperDict({'bozo': 1, 'bozo_exception': err})

    info = common.SuperDict({'status': getattr(ret, 'status', 200)})
    info.href = getattr(ret, 'newurl', obj)
    info.headers = common.SuperDict(getattr(ret, 'headers', {}))
    # Python 3 doesn't normalize header names; Python 2 does
    if info.headers.get('ETag') or info.headers.get('etag'):
        info.etag = info.headers.get('ETag') or info.headers.get('etag')
    if info.headers.get('Last-Modified') or info.headers.get('last-modified'):
        info.modified = info.headers.get('Last-Modified') or \
                        info.headers.get('last-modified')  # noqa: E126
        if isinstance(dates._rfc822(info.modified), datetime.datetime):
            info.modified_parsed = dates._rfc822(info.modified)
    return ret, info


class Injector(object):
    """
    Injector buffers read() calls to a file-like object in order to
    inject a DOCTYPE containing HTML entity definitions immediately
    following the XML declaration.
    """
    def __init__(self, obj):
        self.obj = obj
        self.injected = False
        self.cache = b''

    def read(self, size):
        # Read from the cache (and the object if necessary)
        read = self.cache[:size]
        if len(self.cache) < size:
            read += self.obj.read(size - len(self.cache))
        self.cache = self.cache[size:]

        if self.injected or b'>' not in read:
            return read

        # Inject the entity declarations into the cache
        entities = ''
        for k, v in html_entities.name2codepoint.items():
            entities += '<!ENTITY {0} "&#{1};">'.format(k, v)
        # The '>' is deliberately missing; it will be appended by join()
        doctype = '<!DOCTYPE anyroot [{0}]'.format(entities)
        content = read.split(b'>', 1)
        content.insert(1, b(doctype))
        self.cache = b'>'.join(content)
        self.injected = True

        ret = self.cache[:size]
        self.cache = self.cache[size:]
        return ret

    def __getattr__(self, name):
        return getattr(self.obj, name)


class ListError(Exception):
    """Used when a specification deviation is encountered in an XML file"""
    pass
