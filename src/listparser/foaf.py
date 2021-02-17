# This file is part of listparser.
# Copyright 2009-2021 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import copy

from . import common


class FoafMixin(common.CommonMixin):
    def _start_rdf_RDF(self, attrs):
        self.harvest.version = 'rdf'

    def _start_rss_channel(self, attrs):
        if attrs.get((common._ns['rdf'], 'about'), '').strip():
            # We now have a feed URL, so forget about any opportunity URL
            if self.flag_opportunity:
                self.flag_opportunity = False
                self.agent_opps.pop()
            agent_feed = attrs.get((common._ns['rdf'], 'about')).strip()
            self.agent_feeds.append(agent_feed)

    def _start_ya_feed(self, attrs):
        if attrs.get((common._ns['rdf'], 'resource'), '').strip():
            # This is a feed URL
            agent_feed = attrs[(common._ns['rdf'], 'resource')].strip()
            self.agent_feeds.append(agent_feed)

    def _clean_found_objs(self):
        if self.foaf_name:
            title = self.foaf_name[-1]
        else:
            title = str()
        for url in self.agent_feeds:
            obj = common.SuperDict({'url': url, 'title': title})
            self.group_objs.append(('feeds', obj))
        for url in self.agent_lists:
            obj = common.SuperDict({'url': url, 'title': title})
            self.group_objs.append(('lists', obj))
        for url in self.agent_opps:
            obj = common.SuperDict({'url': url, 'title': title})
            self.group_objs.append(('opportunities', obj))

    def _start_foaf_Agent(self, attrs):
        self.flag_agent = True
        self.flag_feed = True
        self.flag_new_title = True

    def _end_foaf_Agent(self):
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

    def _start_foaf_Person(self, attrs):
        self.flag_feed = True
        self.flag_new_title = True
        self._clean_found_objs()
    _end_foaf_Person = _end_foaf_Agent

    def _start_rdfs_seeAlso(self, attrs):
        if attrs.get((common._ns['rdf'], 'resource'), '').strip():
            # This is a subscription list URL
            agent_list = attrs[(common._ns['rdf'], 'resource')].strip()
            self.agent_lists.append(agent_list)

    def _start_foaf_Group(self, attrs):
        self.flag_group = True

    def _end_foaf_Group(self):
        self.flag_group = False
        for key, obj in self.group_objs:
            # Check for duplicates
            if obj.url in self.found_urls:
                obj = self.found_urls[obj.url][1]
            else:
                self.found_urls[obj.url] = (key, obj)
                self.harvest[key].append(obj)
            # Create or consolidate categories and tags
            obj.setdefault('categories', [])
            obj.setdefault('tags', [])
            if self.hierarchy and self.hierarchy not in obj.categories:
                obj.categories.append(copy.copy(self.hierarchy))
            if len(self.hierarchy) == 1 and \
               self.hierarchy[0] not in obj.tags:
                obj.tags.extend(copy.copy(self.hierarchy))
        self.group_objs = []
        # Maintain the hierarchy
        if self.hierarchy:
            self.hierarchy.pop()
    _end_rdf_RDF = _end_foaf_Group

    _start_foaf_name = common.CommonMixin._expect_characters

    def _end_foaf_name(self):
        value = self._characters.strip()
        if self.flag_feed and self.flag_new_title:
            self.foaf_name.append(value)
            self.flag_new_title = False
        elif self.flag_group and value:
            self.hierarchy.append(value)
            self.flag_group = False

    _start_foaf_member_name = common.CommonMixin._expect_characters
    _end_foaf_member_name = _end_foaf_name

    def _start_foaf_Document(self, attrs):
        if attrs.get((common._ns['rdf'], 'about'), '').strip():
            # Flag this as an opportunity (but ignore if a feed URL is found)
            self.flag_opportunity = True
            agent_opp = attrs.get((common._ns['rdf'], 'about')).strip()
            self.agent_opps.append(agent_opp)
