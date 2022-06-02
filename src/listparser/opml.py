# This file is part of listparser.
# Copyright 2009-2022 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import copy

from . import common
from . import dates


class OpmlMixin(common.CommonMixin):
    def start_opml_opml(self, attrs):
        self.harvest['version'] = 'opml'
        if attrs.get('version') in ('1.0', '1.1'):
            self.harvest['version'] = 'opml1'
        elif attrs.get('version') == '2.0':
            self.harvest['version'] = 'opml2'

    def start_opml_outline(self, attrs):
        url = None
        # Find an appropriate title in @text or @title (else empty)
        if attrs.get('text', '').strip():
            title = attrs['text'].strip()
        else:
            title = attrs.get('title', '').strip()

        # Search for the URL regardless of xmlUrl's case
        for k, v in attrs.items():
            if k.lower() == 'xmlurl':
                url = v.strip()
                break

        append_to = None

        # Determine whether the outline is a feed or subscription list
        if url is not None:
            # It's a feed
            append_to = 'feeds'
            if attrs.get('type', '').strip().lower() == 'source':
                # Actually, it's a subscription list!
                append_to = 'lists'
        elif attrs.get('type', '').lower() in ('link', 'include'):
            # It's a subscription list
            append_to = 'lists'
            url = attrs.get('url', '').strip()
        elif title:
            # Assume that this is a grouping node
            self.hierarchy.append(title)
            return
        # Look for an opportunity URL
        if not url and 'htmlurl' in (k.lower() for k in attrs.keys()):
            for k, v in attrs.items():
                if k.lower() == 'htmlurl':
                    url = v.strip()
            append_to = 'opportunities'
        if not url:
            # Maintain the hierarchy
            self.hierarchy.append('')
            return
        if url not in self.found_urls and append_to:
            # This is a brand new URL
            obj = common.SuperDict({'url': url, 'title': title})
            self.found_urls[url] = (append_to, obj)
            self.harvest[append_to].append(obj)
        else:
            obj = self.found_urls[url][1]

        # Handle categories and tags
        obj.setdefault('categories', [])
        if 'category' in attrs.keys():
            for i in attrs['category'].split(','):
                tmp = [j.strip() for j in i.split('/') if j.strip()]
                if tmp and tmp not in obj['categories']:
                    obj['categories'].append(tmp)
        # Copy the current hierarchy into `categories`
        if self.hierarchy and self.hierarchy not in obj['categories']:
            obj['categories'].append(copy.copy(self.hierarchy))
        # Copy all single-element `categories` into `tags`
        obj['tags'] = [i[0] for i in obj['categories'] if len(i) == 1]

        self.hierarchy.append('')

    def end_opml_outline(self):
        self.hierarchy.pop()

    start_opml_title = common.CommonMixin.expect_text

    def end_opml_title(self):
        value = self.get_text()
        if value:
            self.harvest['meta']['title'] = value

    start_opml_ownerId = common.CommonMixin.expect_text

    def end_opml_ownerId(self):
        value = self.get_text()
        if value:
            self.harvest['meta'].setdefault('author', common.SuperDict())
            self.harvest['meta']['author']['url'] = value

    start_opml_ownerEmail = common.CommonMixin.expect_text

    def end_opml_ownerEmail(self):
        value = self.get_text()
        if value:
            self.harvest['meta'].setdefault('author', common.SuperDict())
            self.harvest['meta']['author']['email'] = value

    start_opml_ownerName = common.CommonMixin.expect_text

    def end_opml_ownerName(self):
        value = self.get_text()
        if value:
            self.harvest['meta'].setdefault('author', common.SuperDict())
            self.harvest['meta']['author']['name'] = value

    start_opml_dateCreated = common.CommonMixin.expect_text

    def end_opml_dateCreated(self):
        value = self.get_text()
        if value:
            self.harvest['meta']['created'] = value
            timestamp = dates.parse_rfc822(value)
            if timestamp:
                self.harvest['meta']['created_parsed'] = timestamp
            else:
                self.raise_bozo('dateCreated is not an RFC 822 datetime')

    start_opml_dateModified = common.CommonMixin.expect_text

    def end_opml_dateModified(self):
        value = self.get_text()
        if value:
            self.harvest['meta']['modified'] = value
            timestamp = dates.parse_rfc822(value)
            if timestamp:
                self.harvest['meta']['modified_parsed'] = timestamp
            else:
                self.raise_bozo('dateModified is not an RFC 822 datetime')
