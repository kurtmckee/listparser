# This file is part of listparser.
# Copyright 2009-2024 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

from __future__ import annotations

import copy
import typing as t

from . import common


class IgoogleMixin(common.Common):
    def start_gtml_gadgettabml(self, _: t.Any) -> None:
        self.harvest["version"] = "igoogle"

    def start_gtml_tab(self, attrs: dict[str, str]) -> None:
        if attrs.get("title", "").strip():
            self.hierarchy.append(attrs["title"].strip())

    def end_gtml_tab(self) -> None:
        if self.hierarchy:
            self.hierarchy.pop()

    def start_igoogle_module(self, attrs: dict[str, str]) -> None:
        if attrs.get("type", "").strip().lower() == "rss":
            self.flag_feed = True

    def end_igoogle_module(self) -> None:
        self.flag_feed = False

    def start_igoogle_moduleprefs(self, attrs: dict[str, str]) -> None:
        if self.flag_feed and attrs.get("xmlurl", "").strip():
            obj = common.SuperDict({"url": attrs["xmlurl"].strip()})
            obj["title"] = ""
            if self.hierarchy:
                obj["categories"] = [copy.copy(self.hierarchy)]
            if len(self.hierarchy) == 1:
                obj["tags"] = copy.copy(self.hierarchy)
            self.harvest["feeds"].append(obj)
