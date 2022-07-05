# This file is part of listparser.
# Copyright 2009-2022 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import html.parser
from typing import Dict, List, Optional, Tuple

from . import common, foaf, igoogle, opml


class LxmlHandler(foaf.FoafMixin, igoogle.IgoogleMixin, opml.OpmlMixin):
    def __init__(self):
        super().__init__()

        # {prefix: uri}
        self.uris: Dict[str, str] = {}

    def start(self, tag: str, attrs: Dict):
        """Handle the start of an XML element."""

        # Extract XML namespaces from the attributes dictionary.
        #
        # The HTML parser converts attribute keys to lowercase.
        #
        # ========================= ===========================
        # Deployed XML              Tuple in `attrs`
        # ========================= ===========================
        # <tag XMLNS="URI">         {"xmlns": "URI"}
        # <tag xmlns:Prefix="uri">  {"xmlns:prefix": "uri"}
        # <tag xmlns>               {"xmlns": ""}
        # ========================= ===========================
        #
        attrs_without_xmlns = {}
        for key, value in attrs.items():
            if key.startswith("xmlns"):
                if value:
                    self.uris[key.partition(":")[2]] = value
            else:
                attrs_without_xmlns[key] = value

        try:
            method = self.start_methods[tag]
        except KeyError:
            # The tag will be in the form "name" or "prefix:name".
            deployed_prefix, _, name = tag.rpartition(":")

            # The deployed prefix used in the XML document is arbitrary,
            # but handler methods are named using standard prefix names.
            # The code below tries to map from the deployed prefix
            # to a declared URI (if any), and then to a standard prefix.
            # However, if there's no URI associated with the prefix,
            # the only identifier available is the deployed prefix itself
            # (which might be an empty string).
            identifier = self.uris.get(
                deployed_prefix, common.uris.get(deployed_prefix, deployed_prefix)
            )
            standard_prefix = common.prefixes.get(identifier, deployed_prefix)
            if standard_prefix:
                method_name = f"start_{standard_prefix}_{name}"
            else:
                method_name = f"start_opml_{name}"
            method = getattr(self, method_name, None)
            self.start_methods[tag] = method

        if method:
            method(attrs_without_xmlns)

    def end(self, tag: str):
        """Handle the end of an XML element."""

        try:
            method = self.end_methods[tag]
        except KeyError:
            deployed_prefix, _, name = tag.rpartition(":")
            identifier = self.uris.get(
                deployed_prefix, common.uris.get(deployed_prefix, deployed_prefix)
            )
            standard_prefix = common.prefixes.get(identifier, deployed_prefix)
            if standard_prefix:
                method_name = f"end_{standard_prefix}_{name}"
            else:
                method_name = f"end_opml_{name}"
            method = getattr(self, method_name, None)
            self.end_methods[tag] = method

        if method:
            method()

    def data(self, data: str):
        """Handle text content of an element."""

        if self.flag_expect_text:
            self.text.append(data)

    def close(self):
        """Reset the handler."""

        super().close()


class HTMLHandler(
    foaf.FoafMixin,
    igoogle.IgoogleMixin,
    opml.OpmlMixin,
    html.parser.HTMLParser,
):
    def __init__(self):
        super().__init__()

        # {prefix: uri}
        self.uris: Dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        """Handle start tags.

        The HTML parser doesn't understand or handle XML namespaces,
        so namespaces are registered as they're encountered.

        Note that XML namespaces are not strictly tracked;
        after a namespace is encountered in a start tag,
        it is never removed when the corresponding end tag is encountered.
        """

        # Extract XML namespaces from the attributes list.
        #
        # The HTML parser converts attribute keys to lowercase.
        #
        # ========================= ===========================
        # Deployed XML              Tuple in `attrs`
        # ========================= ===========================
        # <tag XMLNS="URI">         ("xmlns", "URI")
        # <tag xmlns:Prefix="uri">  ("xmlns:prefix", "uri")
        # <tag xmlns>               ("xmlns", None)
        # ========================= ===========================
        #
        attrs_without_xmlns = {}
        for key, value in attrs:
            if key.startswith("xmlns"):
                if value:
                    self.uris[key.partition(":")[2]] = value
            else:
                attrs_without_xmlns[key] = value

        try:
            # Use a cached start method, if possible.
            method = self.start_methods[tag]
        except KeyError:
            # The tag will be in the form "name" or "prefix:name".
            deployed_prefix, _, name = tag.rpartition(":")

            # The deployed prefix used in the XML document is arbitrary,
            # but handler methods are named using standard prefix names.
            # The code below tries to map from the deployed prefix
            # to a declared URI (if any), and then to a standard prefix.
            # However, if there's no URI associated with the prefix,
            # the only identifier available is the deployed prefix itself
            # (which might be an empty string).
            identifier = self.uris.get(
                deployed_prefix, common.uris.get(deployed_prefix, deployed_prefix)
            )
            standard_prefix = common.prefixes.get(identifier, deployed_prefix)
            if standard_prefix:
                method_name = f"start_{standard_prefix}_{name}"
            else:
                method_name = f"start_opml_{name}"
            method = getattr(self, method_name, None)
            self.start_methods[tag] = method

        if method:
            method(attrs_without_xmlns)

    def handle_endtag(self, tag: str) -> None:
        """Handle end tags."""

        try:
            method = self.end_methods[tag]
        except KeyError:
            deployed_prefix, _, name = tag.rpartition(":")
            identifier = self.uris.get(
                deployed_prefix, common.uris.get(deployed_prefix, deployed_prefix)
            )
            standard_prefix = common.prefixes.get(identifier, deployed_prefix)
            if standard_prefix:
                method_name = f"end_{standard_prefix}_{name}"
            else:
                method_name = f"end_opml_{name}"
            method = getattr(self, method_name, None)
            self.end_methods[tag] = method

        if method:
            method()

    def handle_data(self, data: str) -> None:
        """Handle text content of an element."""

        if self.flag_expect_text:
            self.text.append(data)

    def close(self) -> None:
        """Reset the parser / handler."""

        super().close()
