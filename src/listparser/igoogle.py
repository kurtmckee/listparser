# This file is part of listparser.
# Copyright 2009-2022 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import copy

from . import common


class IgoogleMixin(common.CommonMixin):
    def start_gtml_gadgettabml(self, _):
        self.harvest["version"] = "igoogle"

    def start_gtml_tab(self, attrs):
        if attrs.get("title", "").strip():
            self.hierarchy.append(attrs["title"].strip())

    def end_gtml_tab(self):
        if self.hierarchy:
            self.hierarchy.pop()

    def start_igoogle_module(self, attrs):
        if attrs.get("type", "").strip().lower() == "rss":
            self.flag_feed = True

    def end_igoogle_module(self):
        self.flag_feed = False

    def start_igoogle_moduleprefs(self, attrs):
        if self.flag_feed and attrs.get("xmlurl", "").strip():
            obj = common.SuperDict({"url": attrs["xmlurl"].strip()})
            obj["title"] = ""
            if self.hierarchy:
                obj["categories"] = [copy.copy(self.hierarchy)]
            if len(self.hierarchy) == 1:
                obj["tags"] = copy.copy(self.hierarchy)
            self.harvest["feeds"].append(obj)
