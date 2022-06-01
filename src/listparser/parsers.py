# This file is part of listparser.
# Copyright 2009-2022 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

from typing import Dict, Tuple
import xml.sax

try:
    import lxml.etree
except ImportError:
    lxml = None

from . import common
from . import foaf
from . import igoogle
from . import opml


class LxmlHandler(foaf.FoafMixin, igoogle.IgoogleMixin, opml.OpmlMixin):
    def start(self, name: str, attrs: Dict):
        """Handle the start of an XML element."""

        try:
            method = self.start_methods[name]
        except KeyError:
            namespace, _, tag = name.rpartition('}')
            namespace = namespace[1:]
            try:
                function = f'start_{common.namespaces[namespace]}_{tag}'
            except KeyError:
                function = f'start_opml_{tag}'
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
                function = f'end_{common.namespaces[namespace]}_{tag}'
            except KeyError:
                function = f'end_opml_{tag}'
            self.end_methods[name] = method = getattr(self, function, None)

        if method:
            method()

    def data(self, data: str):
        """Handle text content of an element."""

        if self.flag_expect_text:
            self.text.append(data)

    def close(self):
        pass


class XmlSaxHandler(
    foaf.FoafMixin,
    igoogle.IgoogleMixin,
    opml.OpmlMixin,
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

    error = warning
    fatalError = warning

    # ContentHandler methods
    # ----------------------

    def startElementNS(self, name: Tuple[str, str], qname: str, attrs):
        """Handle the start of an XML element.

        Attribute keys will be converted from tuples of strings
        to strings to match the format that lxml uses.
        """

        try:
            method = self.start_methods[name]
        except KeyError:
            fn = ''
            if name[0] in common.namespaces:
                fn = f'start_{common.namespaces[name[0]]}_{name[1]}'
            elif name[0] is None:
                fn = f'start_opml_{name[1]}'
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
                fn = f'end_{common.namespaces[name[0]]}_{name[1]}'
            elif name[0] is None:
                fn = f'end_opml_{name[1]}'
            self.end_methods[name] = method = getattr(self, fn, None)

        if method:
            method()

    def characters(self, content):
        if self.flag_expect_text:
            self.text.append(content)


if lxml:
    Handler = LxmlHandler
else:
    Handler = XmlSaxHandler
