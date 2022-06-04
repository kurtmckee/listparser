# This file is part of listparser.
# Copyright 2009-2022 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import copy

from . import common


class IgoogleMixin(common.CommonMixin):
    def start_gtml_GadgetTabML(self, _):
        self.harvest['version'] = 'igoogle'

    def start_gtml_Tab(self, attrs):
        if attrs.get('title', '').strip():
            self.hierarchy.append(attrs['title'].strip())

    def end_gtml_Tab(self):
        if self.hierarchy:
            self.hierarchy.pop()

    def start_iGoogle_Module(self, attrs):
        if attrs.get('type', '').strip().lower() == 'rss':
            self.flag_feed = True

    def end_iGoogle_Module(self):
        self.flag_feed = False

    def start_iGoogle_ModulePrefs(self, attrs):
        if self.flag_feed and attrs.get('xmlUrl', '').strip():
            obj = common.SuperDict({'url': attrs['xmlUrl'].strip()})
            obj['title'] = ''
            if self.hierarchy:
                obj['categories'] = [copy.copy(self.hierarchy)]
            if len(self.hierarchy) == 1:
                obj['tags'] = copy.copy(self.hierarchy)
            self.harvest['feeds'].append(obj)
