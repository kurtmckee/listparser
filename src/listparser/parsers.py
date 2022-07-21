# This file is part of listparser.
# Copyright 2009-2022 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

from __future__ import annotations

import collections
import dataclasses
import html.parser

from . import common, foaf, igoogle, opml


@dataclasses.dataclass
class Node:
    """Track information parsed from start tags.

    When a handler method for an end tag is called,
    it will use this information to manage the namespace stack.
    """

    tag: str
    standard_prefix: str
    name: str
    namespace_prefixes: set[str]


class LxmlHandler(foaf.FoafMixin, igoogle.IgoogleMixin, opml.OpmlMixin):
    def __init__(self):
        super().__init__()

        # {prefix: [uri1, ...]}
        self.uris: dict[str, list[str]] = {}
        self.node_stack: collections.deque[Node] = collections.deque()

    def start(self, tag: str, attrs: dict[str, str]):
        """Handle the start of an XML element."""

        # Extract XML namespaces from the attributes dictionary.
        #
        # The HTML parser converts attribute keys to lowercase.
        #
        # ========================= ===========================
        # Deployed XML              Key/value in *attrs*
        # ========================= ===========================
        # <tag XMLNS="URI">         {"xmlns": "URI"}
        # <tag xmlns:Prefix="uri">  {"xmlns:prefix": "uri"}
        # <tag xmlns>               {"xmlns": ""}
        # ========================= ===========================
        #
        attrs_excluding_xmlns = {}
        namespace_prefixes = set()
        for key, value in attrs.items():
            if key.startswith("xmlns"):
                if value:
                    _, _, declared_prefix = key.partition(":")
                    self.uris.setdefault(declared_prefix, []).append(value)
                    namespace_prefixes.add(declared_prefix)
            else:
                attrs_excluding_xmlns[key] = value

        # The tag will be in the form "name" or "prefix:name".
        deployed_prefix, _, name = tag.rpartition(":")

        # The deployed prefix used in the XML document is arbitrary,
        # but handler methods are named using standard prefix names.
        # The code below tries to map from the deployed prefix
        # to a declared URI (if any), and then to a standard prefix.
        # However, if there's no URI associated with the prefix,
        # the only identifier available is the deployed prefix itself
        # (which might be an empty string).
        identifier_list = self.uris.get(
            deployed_prefix, [common.uris.get(deployed_prefix, deployed_prefix)]
        )
        if identifier_list:
            identifier = identifier_list[-1]
        else:
            identifier = "= sentinel: no identifier ="
        standard_prefix = common.prefixes.get(identifier, deployed_prefix)

        # Namespaces must be associated with the tags that introduce them
        # so the corresponding end tag can remove them from the list.
        node = Node(
            tag=tag,
            standard_prefix=standard_prefix,
            name=name,
            namespace_prefixes=namespace_prefixes,
        )
        self.node_stack.append(node)

        try:
            start_method = self.start_methods[(standard_prefix, name)]
        except KeyError:
            if standard_prefix:
                start_method_name = f"start_{standard_prefix}_{name}"
                end_method_name = f"end_{standard_prefix}_{name}"
            else:
                start_method_name = f"start_opml_{name}"
                end_method_name = f"end_opml_{name}"
            start_method = getattr(self, start_method_name, None)
            end_method = getattr(self, end_method_name, None)
            self.start_methods[(standard_prefix, name)] = start_method
            self.end_methods[(standard_prefix, name)] = end_method

        if start_method is not None:
            start_method(attrs_excluding_xmlns)

    def end(self, tag: str):
        """Handle the end of an XML element."""

        while True:
            try:
                node = self.node_stack.pop()
            except IndexError:
                deployed_prefix, _, name = tag.rpartition(":")
                identifier_list = self.uris.get(
                    deployed_prefix, [common.uris.get(deployed_prefix, deployed_prefix)]
                )
                if identifier_list:
                    identifier = identifier_list[-1]
                else:
                    identifier = "= sentinel: no identifier ="
                standard_prefix = common.prefixes.get(identifier, deployed_prefix)
                node = Node(
                    tag=tag,
                    standard_prefix=standard_prefix,
                    name=name,
                    namespace_prefixes=set(),
                )

            for prefix in node.namespace_prefixes:
                try:
                    self.uris[prefix].pop()
                except LookupError:
                    pass

            end_method = self.end_methods.get((node.standard_prefix, node.name))
            if end_method is not None:
                end_method()

            if node.tag == tag:
                break

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
        self.uris: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
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
        # Deployed XML              Tuple in *attrs*
        # ========================= ===========================
        # <tag XMLNS="URI">         ("xmlns", "URI")
        # <tag xmlns:Prefix="uri">  ("xmlns:prefix", "uri")
        # <tag xmlns>               ("xmlns", None)
        # ========================= ===========================
        #
        attrs_excluding_xmlns = {}
        for key, value in attrs:
            if key.startswith("xmlns"):
                if value:
                    _, _, declared_prefix = key.partition(":")
                    self.uris[declared_prefix] = value
            else:
                attrs_excluding_xmlns[key] = value

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

        try:
            # Use a cached start method, if possible.
            method = self.start_methods[(standard_prefix, name)]
        except KeyError:
            if standard_prefix:
                method_name = f"start_{standard_prefix}_{name}"
            else:
                method_name = f"start_opml_{name}"
            method = getattr(self, method_name, None)
            self.start_methods[(standard_prefix, name)] = method

        if method:
            method(attrs_excluding_xmlns)

    def handle_endtag(self, tag: str) -> None:
        """Handle end tags."""

        deployed_prefix, _, name = tag.rpartition(":")
        identifier = self.uris.get(
            deployed_prefix, common.uris.get(deployed_prefix, deployed_prefix)
        )
        standard_prefix = common.prefixes.get(identifier, deployed_prefix)

        try:
            method = self.end_methods[(standard_prefix, name)]
        except KeyError:
            if standard_prefix:
                method_name = f"end_{standard_prefix}_{name}"
            else:
                method_name = f"end_opml_{name}"
            method = getattr(self, method_name, None)
            self.end_methods[(standard_prefix, name)] = method

        if method:
            method()

    def handle_data(self, data: str) -> None:
        """Handle text content of an element."""

        if self.flag_expect_text:
            self.text.append(data)

    def close(self) -> None:
        """Reset the parser / handler."""

        super().close()
