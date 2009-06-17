# listparser.py - Parse OPML subscription lists into a negotiable format.
# Copyright (C) 2009 Kurt McKee <contactme@kurtmckee.org>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib2
import xml.sax

def parse(filename_or_url):
    try:
        f = urllib2.urlopen(filename_or_url)
    except:
        return {}
    handler = Handler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.setErrorHandler(handler)
    parser.parse(f)
    f.close()

    return handler.harvest

class Handler(xml.sax.handler.ContentHandler, xml.sax.handler.ErrorHandler):
    def __init__(self):
        self.harvest = {'bozo': 0}
        self.expect = ''

    # ErrorHandler functions
    # ----------------------
    def warning(self, exception):
        self.harvest['bozo'] = 1
        self.harvest['bozo_detail'] = repr(exception)
        return
    error = warning
    fatalError = warning

    # ContentHandler functions
    # ------------------------
    def startElement(self, name, attrs):
        if hasattr(self, '_start_%s' % name):
            getattr(self, '_start_%s' % name)(attrs)
    def endElement(self, name):
        if hasattr(self, '_end_%s' % name):
            getattr(self, '_end_%s' % name)()
    def characters(self, content):
        if not self.expect:
            return
        # If `expect` contains something like "userinfo_contact_email_domain",
        # then after these next lines, node will point to the nested dictionary
        # `self.harvest['userinfo']['contact']['email']`, and
        # `...['email']['domain']` will be filled with `content`.
        node = reduce(lambda x, y: x.setdefault(y, {}), self.expect.split('_')[:-1], self.harvest)
        node[self.expect.split('_')[-1]] = node.setdefault(self.expect.split('_')[-1], '') + content
    def endExpect(self):
        self.expect = ''
    def _start_opml(self, attrs):
        self.harvest['version'] = "opml"
        if attrs.has_key('version'):
            if attrs['version'] in ("1.0", "1.1"):
                self.harvest['version'] = "opml1"
            elif attrs['version'] == "2.0":
                self.harvest['version'] = "opml2"
            else:
                self.harvest['bozo'] = 1
                self.harvest['bozo_detail'] = "Unknown OPML version"
    def _start_outline(self, attrs):
        if 'xmlurl' in [i.lower() for i in attrs.keys()]:
            if not attrs.has_key('type'):
                self.harvest['bozo'] = 1
                self.harvest['bozo_detail'] = "<outline> MUST have a `type` attribute"
            if attrs.has_key('type') and attrs['type'].lower() not in ('rss', 'pie'):
                return
            if not attrs.has_key('xmlUrl'):
                self.harvest['bozo'] = 1
                self.harvest['bozo_detail'] = "Only `xmlUrl` EXACTLY is valid"
            # This list comprehension selects the `xmlUrl` attribute no matter its case
            xmlurl = attrs[[i for i in attrs.keys() if i.lower() == "xmlurl"][0]]
            if attrs.has_key('text'):
                name = attrs['text']
            else:
                self.harvest['bozo'] = 1
                self.harvest['bozo_detail'] = "An <outline> has no `text` attribute"
                if attrs.has_key('title'):
                    name = attrs['title']
                else:
                    name = xmlurl
            self.harvest.setdefault('feeds', []).append({
                'name': name,
                'url': xmlurl,
            })
    def _start_title(self, attrs):
        self.expect = 'meta_title'
    _end_title = endExpect
    def _start_ownerId(self, attrs):
        self.expect = 'meta_author_url'
    _end_ownerId = endExpect
    def _start_ownerEmail(self, attrs):
        self.expect = 'meta_author_email'
    _end_ownerEmail = endExpect
    def _start_ownerName(self, attrs):
        self.expect = 'meta_author_name'
    _end_ownerName = endExpect
