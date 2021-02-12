# listparser - Parse OPML, FOAF, and iGoogle subscription lists.
# Copyright 2009-2021 Kurt McKee <contactme@kurtmckee.org>
#
# This file is part of listparser.
#
# listparser is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# listparser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with listparser.  If not, see <http://www.gnu.org/licenses/>.

import copy

from . import common


class IgoogleMixin(common.CommonMixin):
    def _start_gtml_GadgetTabML(self, attrs):
        self.harvest.version = 'igoogle'

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
            obj.title = ''
            if self.hierarchy:
                obj.categories = [copy.copy(self.hierarchy)]
            if len(self.hierarchy) == 1:
                obj.tags = copy.copy(self.hierarchy)
            self.harvest.feeds.append(obj)
