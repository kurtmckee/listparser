# This file is part of listparser.
# Copyright 2009-2024 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

from __future__ import annotations

import typing as t

from .exceptions import ListparserError
from .xml_handler import XMLHandler


class SuperDict(t.Dict[str, t.Any]):
    """
    SuperDict is a dictionary object with keys posing as instance attributes.

    ..  code-block:: pycon

        >>> i = SuperDict()
        >>> i.one = 1
        >>> i
        {'one': 1}

    """

    def __getattribute__(self, name: str) -> t.Any:
        if name in self:
            return self[name]
        else:
            return dict.__getattribute__(self, name)


class Common(XMLHandler):
    def __init__(self) -> None:
        super().__init__()
        self.harvest: dict[str, t.Any] = {}
        self.hierarchy: list[str] = []
        self.flag_feed = False

        # found_urls = {url: (append_to_key, obj)}
        self.found_urls: dict[str, tuple[str, SuperDict]] = {}

    def raise_bozo(self, error: str) -> None:
        self.harvest["bozo"] = True
        self.harvest["bozo_exception"] = ListparserError(error)

    def expect_text(self, _: t.Any) -> None:
        """Flag that text content is anticipated.

        Many start_* methods only need to prepare for text content.
        This method exists so those start_* methods can be declared
        as aliases for this method.
        """

        self.flag_expect_text = True
        self.text = []

    def get_text(self) -> str:
        """Get text content."""

        text = "".join(self.text).strip()
        self.text = []
        return text

    def close(self) -> None:
        super().close()
        self.hierarchy = []
        self.flag_feed = False
        self.found_urls = {}
