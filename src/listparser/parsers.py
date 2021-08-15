# This file is part of listparser.
# Copyright 2009-2021 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

from typing import Callable, Dict, Tuple, Union
import xml.sax

try:
    import lxml.etree
except ImportError:
    lxml = None

from . import common
from . import exceptions
from . import foaf
from . import igoogle
from . import opml


class BaseHandler(foaf.FoafMixin, igoogle.IgoogleMixin, opml.OpmlMixin):
    def __init__(self):
        super().__init__()
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

        # Cache element-to-method name lookups.
        #
        # The dictionary key types vary between parsers:
        #
        # If LXML is the parser, the keys will be strings.
        # If xml.sax is the parser, the keys will be tuples of strings.
        #
        self.start_methods: Dict[Union[Tuple[str, str], str], Callable] = {}
        self.end_methods: Dict[Union[Tuple[str, str], str], Callable] = {}

    def raise_bozo(self, error: str):
        self.harvest['bozo'] = True
        if isinstance(error, str):
            self.harvest['bozo_exception'] = exceptions.ListparserError(error)
        else:
            self.harvest['bozo_exception'] = error


class LxmlHandler(BaseHandler):
    def start(self, name: str, attrs: Dict):
        """Handle the start of an XML element."""

        try:
            method = self.start_methods[name]
        except KeyError:
            namespace, _, tag = name.rpartition('}')
            namespace = namespace[1:]
            try:
                function = f'_start_{common.namespaces[namespace]}_{tag}'
            except KeyError:
                function = f'_start_opml_{tag}'
            self.start_methods[name] = method = getattr(self, function, None)

        if method:
            method(attrs)

    def end(self, name: str):
        """Handle the end of an XML element."""

        try:
            method = self.end_methods[name]
        except KeyError:
            namespace, _, tag = name.rpartition('}')
            namespace = namespace[1:]
            try:
                function = f'_end_{common.namespaces[namespace]}_{tag}'
            except KeyError:
                function = f'_end_opml_{tag}'
            self.end_methods[name] = method = getattr(self, function, None)

        if method:
            method()

            # Always disable and reset character capture in order to
            # reduce code duplication in the _end_opml_* functions.
            self.expect = False
            self._characters = str()

    def data(self, data: str):
        """Handle text content of an element."""

        if self.expect:
            self._characters += data

    def close(self):
        pass


class XmlSaxHandler(
    BaseHandler,
    xml.sax.handler.ContentHandler,
    xml.sax.handler.ErrorHandler,
):
    def __init__(self):
        super().__init__()
        xml.sax.handler.ContentHandler.__init__(self)
        xml.sax.handler.ErrorHandler.__init__(self)

    # ErrorHandler methods
    # --------------------

    def warning(self, exception):
        self.raise_bozo(exception)
        return

    error = warning
    fatalError = warning

    # ContentHandler methods
    # ----------------------

    def startElementNS(self, name: Tuple[str, str], qname: str, attrs):
        """Handle the start of an XML element.

        Attribute keys will be converted from tuples of strings
        to strings to match the format that LXML uses.
        """

        try:
            method = self.start_methods[name]
        except KeyError:
            fn = ''
            if name[0] in common.namespaces:
                fn = f'_start_{common.namespaces[name[0]]}_{name[1]}'
            elif name[0] is None:
                fn = f'_start_opml_{name[1]}'
            self.start_methods[name] = method = getattr(self, fn, None)

        if not method:
            return

        # Convert the keys in *attrs* from tuples to strings:
        #
        #     {(uri, localname): value}
        #     {"{uri}localname": value}
        #
        attributes = {}
        for (uri, localname), value in attrs.items():
            if uri:
                attributes[f'{{{uri}}}{localname}'] = value
            else:
                attributes[localname] = value

        method(attributes)

    def endElementNS(self, name: Tuple[str, str], qname: str):
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


if lxml:
    Handler = LxmlHandler
else:
    Handler = XmlSaxHandler
