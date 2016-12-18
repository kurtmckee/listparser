# listparser - Parse OPML, FOAF, and iGoogle subscription lists.
# Copyright 2009-2016 Kurt McKee <contactme@kurtmckee.org>
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

from __future__ import absolute_import
from __future__ import unicode_literals

import copy
import datetime

from . import common
from . import dates


class OpmlMixin(common.CommonMixin):
    def _start_opml_opml(self, attrs):
        self.harvest.version = 'opml'
        if attrs.get((None, 'version')) in ('1.0', '1.1'):
            self.harvest.version = 'opml1'
        elif attrs.get((None, 'version')) == '2.0':
            self.harvest.version = 'opml2'

    def _start_opml_outline(self, attrs):
        url = None
        # Find an appropriate title in @text or @title (else empty)
        if attrs.get((None, 'text'), '').strip():
            title = attrs[(None, 'text')].strip()
        else:
            title = attrs.get((None, 'title'), '').strip()

        # Search for the URL regardless of xmlUrl's case
        for k, v in attrs.items():
            if k[1].lower() == 'xmlurl':
                url = v.strip()
                break
        # Determine whether the outline is a feed or subscription list
        if url is not None:
            # It's a feed
            append_to = 'feeds'
            if attrs.get((None, 'type'), '').strip().lower() == 'source':
                # Actually, it's a subscription list!
                append_to = 'lists'
        elif attrs.get((None, 'type'), '').lower() in ('link', 'include'):
            # It's a subscription list
            append_to = 'lists'
            url = attrs.get((None, 'url'), '').strip()
        elif title:
            # Assume that this is a grouping node
            self.hierarchy.append(title)
            return
        # Look for an opportunity URL
        if not url and 'htmlurl' in (k[1].lower() for k in attrs.keys()):
            for k, v in attrs.items():
                if k[1].lower() == 'htmlurl':
                    url = v.strip()
            append_to = 'opportunities'
        if not url:
            # Maintain the hierarchy
            self.hierarchy.append('')
            return
        if url not in self.found_urls:
            # This is a brand new URL
            obj = common.SuperDict({'url': url, 'title': title})
            self.found_urls[url] = (append_to, obj)
            self.harvest[append_to].append(obj)
        else:
            obj = self.found_urls[url][1]

        # Handle categories and tags
        obj.setdefault('categories', [])
        if (None, 'category') in attrs.keys():
            for i in attrs[(None, 'category')].split(','):
                tmp = [j.strip() for j in i.split('/') if j.strip()]
                if tmp and tmp not in obj.categories:
                    obj.categories.append(tmp)
        # Copy the current hierarchy into `categories`
        if self.hierarchy and self.hierarchy not in obj.categories:
            obj.categories.append(copy.copy(self.hierarchy))
        # Copy all single-element `categories` into `tags`
        obj.tags = [i[0] for i in obj.categories if len(i) == 1]

        self.hierarchy.append('')

    def _end_opml_outline(self):
        self.hierarchy.pop()

    _start_opml_title = common.CommonMixin._expect_characters

    def _end_opml_title(self):
        if self.normchars():
            self.harvest.meta.title = self.normchars()

    _start_opml_ownerId = common.CommonMixin._expect_characters

    def _end_opml_ownerId(self):
        if self.normchars():
            self.harvest.meta.setdefault('author', common.SuperDict())
            self.harvest.meta.author.url = self.normchars()

    _start_opml_ownerEmail = common.CommonMixin._expect_characters

    def _end_opml_ownerEmail(self):
        if self.normchars():
            self.harvest.meta.setdefault('author', common.SuperDict())
            self.harvest.meta.author.email = self.normchars()

    _start_opml_ownerName = common.CommonMixin._expect_characters

    def _end_opml_ownerName(self):
        if self.normchars():
            self.harvest.meta.setdefault('author', common.SuperDict())
            self.harvest.meta.author.name = self.normchars()

    _start_opml_dateCreated = common.CommonMixin._expect_characters

    def _end_opml_dateCreated(self):
        if self.normchars():
            self.harvest.meta.created = self.normchars()
            d = dates._rfc822(self.harvest.meta.created)
            if isinstance(d, datetime.datetime):
                self.harvest.meta.created_parsed = d
            else:
                self.raise_bozo('dateCreated is not an RFC 822 datetime')

    _start_opml_dateModified = common.CommonMixin._expect_characters

    def _end_opml_dateModified(self):
        if self.normchars():
            self.harvest.meta.modified = self.normchars()
            d = dates._rfc822(self.harvest.meta.modified)
            if isinstance(d, datetime.datetime):
                self.harvest.meta.modified_parsed = d
            else:
                self.raise_bozo('dateModified is not an RFC 822 datetime')
