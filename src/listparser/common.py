# This file is part of listparser.
# Copyright 2009-2022 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

from typing import Dict, Tuple

from .exceptions import ListparserError
from .xml_handler import XMLHandler


class SuperDict(dict):
    """
    SuperDict is a dictionary object with keys posing as instance attributes.

    ..  code-block:: pycon

        >>> i = SuperDict()
        >>> i.one = 1
        >>> i
        {'one': 1}

    """

    def __getattribute__(self, name):
        if name in self:
            return self[name]
        else:
            return dict.__getattribute__(self, name)


class Common(XMLHandler):
    def __init__(self):
        super().__init__()
        self.harvest = {}
        self.hierarchy = []
        self.flag_feed = False

        # found_urls = {url: (append_to_key, obj)}
        self.found_urls: Dict[str, Tuple[str, SuperDict]] = {}

    def raise_bozo(self, error: str):
        self.harvest["bozo"] = True
        self.harvest["bozo_exception"] = ListparserError(error)

    def expect_text(self, _):
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

    def close(self):
        super().close()
        self.hierarchy = []
        self.flag_feed = False
        self.found_urls = {}
