# This file is part of listparser.
# Copyright 2009-2024 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

from __future__ import annotations

import copy
import typing as t

from . import common

# Attribute key constants
RDF_ABOUT = "rdf:about"
RDF_RESOURCE = "rdf:resource"


class FoafMixin(common.Common):
    def __init__(self) -> None:
        super().__init__()

        self.flag_agent = False
        self.flag_group = False
        self.flag_new_title = False
        self.flag_opportunity = False
        # group_objs = [(append_to_key, obj)]
        self.group_objs: list[tuple[str, common.SuperDict]] = []
        self.agent_feeds: list[str] = []
        self.agent_lists: list[str] = []
        self.agent_opps: list[str] = []
        self.foaf_name: list[str] = []

    def close(self) -> None:
        super().close()
        self.flag_agent = False
        self.flag_group = False
        self.flag_new_title = False
        self.flag_opportunity = False
        self.group_objs = []
        self.agent_feeds = []
        self.agent_lists = []
        self.agent_opps = []
        self.foaf_name = []

    def start_rdf_rdf(self, _: t.Any) -> None:
        self.harvest["version"] = "rdf"

    def start_rss_channel(self, attrs: dict[str, str]) -> None:
        if attrs.get(RDF_ABOUT, "").strip():
            # We now have a feed URL, so forget about any opportunity URL.
            if self.flag_opportunity:
                self.flag_opportunity = False
                self.agent_opps.pop()
            agent_feed = attrs[RDF_ABOUT].strip()
            self.agent_feeds.append(agent_feed)

    def start_ya_feed(self, attrs: dict[str, str]) -> None:
        if attrs.get(RDF_RESOURCE, "").strip():
            # This is a feed URL
            agent_feed = attrs[RDF_RESOURCE].strip()
            self.agent_feeds.append(agent_feed)

    def _clean_found_objs(self) -> None:
        if self.foaf_name:
            title = self.foaf_name[-1]
        else:
            title = ""
        for url in self.agent_feeds:
            obj = common.SuperDict({"url": url, "title": title})
            self.group_objs.append(("feeds", obj))
        for url in self.agent_lists:
            obj = common.SuperDict({"url": url, "title": title})
            self.group_objs.append(("lists", obj))
        for url in self.agent_opps:
            obj = common.SuperDict({"url": url, "title": title})
            self.group_objs.append(("opportunities", obj))

    def start_foaf_agent(self, _: t.Any) -> None:
        self.flag_agent = True
        self.flag_feed = True
        self.flag_new_title = True

    def end_foaf_agent(self) -> None:
        if self.flag_agent:
            self.flag_agent = False
        self._clean_found_objs()
        if self.foaf_name:
            self.foaf_name.pop()
        self.agent_feeds = []
        self.agent_lists = []
        self.agent_opps = []
        self.flag_agent = False
        self.flag_feed = False
        self.flag_opportunity = False

    def start_foaf_person(self, _: t.Any) -> None:
        self.flag_feed = True
        self.flag_new_title = True
        self._clean_found_objs()

    end_foaf_person = end_foaf_agent

    def start_rdfs_seealso(self, attrs: dict[str, str]) -> None:
        if attrs.get(RDF_RESOURCE, "").strip():
            # This is a subscription list URL
            agent_list = attrs[RDF_RESOURCE].strip()
            self.agent_lists.append(agent_list)

    def start_foaf_group(self, _: t.Any) -> None:
        self.flag_group = True

    def end_foaf_group(self) -> None:
        self.flag_group = False
        for key, obj in self.group_objs:
            # Check for duplicates
            if obj["url"] in self.found_urls:
                obj = self.found_urls[obj["url"]][1]
            else:
                self.found_urls[obj["url"]] = (key, obj)
                self.harvest[key].append(obj)
            # Create or consolidate categories and tags
            obj.setdefault("categories", [])
            obj.setdefault("tags", [])
            if self.hierarchy and self.hierarchy not in obj["categories"]:
                obj["categories"].append(copy.copy(self.hierarchy))
            if len(self.hierarchy) == 1 and self.hierarchy[0] not in obj["tags"]:
                obj["tags"].extend(copy.copy(self.hierarchy))
        self.group_objs = []
        # Maintain the hierarchy
        if self.hierarchy:
            self.hierarchy.pop()

    end_rdf_rdf = end_foaf_group

    start_foaf_name = common.Common.expect_text

    def end_foaf_name(self) -> None:
        value = self.get_text()
        if self.flag_feed and self.flag_new_title:
            self.foaf_name.append(value)
            self.flag_new_title = False
        elif self.flag_group and value:
            self.hierarchy.append(value)
            self.flag_group = False

    start_foaf_member_name = common.Common.expect_text
    end_foaf_member_name = end_foaf_name

    def start_foaf_document(self, attrs: dict[str, str]) -> None:
        if attrs.get(RDF_ABOUT, "").strip():
            # Flag this as an opportunity (but ignore if a feed URL is found).
            self.flag_opportunity = True
            agent_opp = attrs[RDF_ABOUT].strip()
            self.agent_opps.append(agent_opp)
