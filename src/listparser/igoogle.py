# This file is part of listparser.
# Copyright 2009-2021 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import copy

from . import common


class IgoogleMixin(common.CommonMixin):
    def _start_gtml_GadgetTabML(self, attrs):
        self.harvest['version'] = 'igoogle'

    def _start_gtml_Tab(self, attrs):
        if attrs.get((None, 'title'), '').strip():
            self.hierarchy.append(attrs[(None, 'title')].strip())

    def _end_gtml_Tab(self):
        if self.hierarchy:
            self.hierarchy.pop()

    def _start_iGoogle_Module(self, attrs):
        if attrs.get((None, 'type'), '').strip().lower() == 'rss':
            self.flag_feed = True

    def _end_iGoogle_Module(self):
        self.flag_feed = False

    def _start_iGoogle_ModulePrefs(self, attrs):
        if self.flag_feed and attrs.get((None, 'xmlUrl'), '').strip():
            obj = common.SuperDict({'url': attrs[(None, 'xmlUrl')].strip()})
            obj['title'] = ''
            if self.hierarchy:
                obj['categories'] = [copy.copy(self.hierarchy)]
            if len(self.hierarchy) == 1:
                obj['tags'] = copy.copy(self.hierarchy)
            self.harvest['feeds'].append(obj)
