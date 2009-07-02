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

__version__ = "0.2"

import datetime
import re
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

    if handler.harvest.get('meta', {}).get('created', '').strip():
        d = _rfc822(handler.harvest['meta']['created'].strip())
        if d:
            handler.harvest['meta']['created_parsed'] = d
        else:
            handler.harvest['bozo'] = 1
            handler.harvest['bozo_detail'] = "dateCreated is not a valid datetime"
    if handler.harvest.get('meta', {}).get('modified', '').strip():
        d = _rfc822(handler.harvest['meta']['modified'].strip())
        if d:
            handler.harvest['meta']['modified_parsed'] = d
        else:
            handler.harvest['bozo'] = 1
            handler.harvest['bozo_detail'] = "dateModified is not a valid datetime"

    return handler.harvest

class Handler(xml.sax.handler.ContentHandler, xml.sax.handler.ErrorHandler):
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
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
        else:
            self.harvest['bozo'] = 1
            self.harvest['bozo_detail'] = "<opml> MUST have a version attribute"
    def _start_outline(self, attrs):
        if 'xmlurl' in (i.lower() for i in attrs.keys()):
            feed = dict()
            if not attrs.has_key('type'):
                self.harvest['bozo'] = 1
                self.harvest['bozo_detail'] = "<outline> MUST have a `type` attribute"
            if attrs.has_key('type') and attrs['type'].lower() not in ('rss', 'pie'):
                self.harvest['bozo'] = 1
                self.harvest['bozo_detail'] = "//outline/@type is not recognized"
            if not attrs.has_key('xmlUrl'):
                self.harvest['bozo'] = 1
                self.harvest['bozo_detail'] = "Only `xmlUrl` EXACTLY is valid"
            # This generator expression selects the `xmlUrl` attribute no matter its case
            feed['url'] = (v for k, v in attrs.items() if k.lower() == "xmlurl").next()
            # Fill feed['title'] with either @text, @title, or @xmlurl, in that order
            if attrs.has_key('text'):
                feed['title'] = attrs['text']
            else:
                self.harvest['bozo'] = 1
                self.harvest['bozo_detail'] = "An <outline> has no `text` attribute"
                if attrs.has_key('title'):
                    feed['title'] = attrs['title']
                else:
                    feed['title'] = feed['url']
            # Fill feed['claims'] up with information that is *purported* to
            # be duplicated from the feed itself.
            for k in ('htmlUrl', 'title', 'description'):
                if attrs.has_key(k):
                    feed.setdefault('claims', {})[k] = attrs[k]
            self.harvest.setdefault('feeds', []).append(feed)
        # Subscription lists
        elif attrs.has_key('type') and attrs['type'].lower() in ('link', 'include'):
            if not attrs.has_key('url'):
                self.harvest['bozo'] = 1
                self.harvest['bozo_detail'] = "`link` and `include` types MUST has a `url` attribute"
                return
            sublist = dict()
            if attrs['type'].lower() == 'link' and not attrs['url'].endswith('.opml'):
                self.harvest['bozo'] = 1
                self.harvest['bozo_detail'] = "`link` types' `url` attribute MUST end with '.opml'"
            sublist['url'] = attrs['url']
            if attrs.has_key('text'):
                sublist['title'] = attrs['text']
            else:
                self.harvest['bozo'] = 1
                self.harvest['bozo_detail'] = "outlines MUST have a `text` attribute"
                sublist['title'] = sublist['url']
            self.harvest.setdefault('lists', []).append(sublist)
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
    def _start_dateCreated(self, attrs):
        self.expect = 'meta_created'
    _end_dateCreated = endExpect
    def _start_dateModified(self, attrs):
        self.expect = 'meta_modified'
    _end_dateModified = endExpect

def _rfc822(date):
    """Parse RFC 822 dates and times, with one minor
    difference: years may be 4DIGIT or 2DIGIT.
    http://tools.ietf.org/html/rfc822#section-5"""
    month_ = "(?P<month>jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
    year_ = "(?P<year>(?:\d{2})?\d{2})"
    day_ = "(?P<day>\d{2})"
    date_ = "%s %s %s" % (day_, month_, year_)
    
    hour_ = "(?P<hour>\d{2}):(?P<minute>\d{2})(?::(?P<second>\d{2}))?"
    tz_ = "(?P<tz>ut|gmt|[ecmp][sd]t|[zamny]|[+-]\d{4})"
    time_ = "%s %s" % (hour_, tz_)

    dayname_ = "(?P<dayname>mon|tue|wed|thu|fri|sat|sun)"
    dt_ = "(?:%s, )?%s %s" % (dayname_, date_, time_)

    try:
        m = re.match(dt_, date.lower()).groupdict(0)
    except:
        return None
    # directly convert everything listed into an int
    m.update((x, int(m[x])) for x in ('year', 'day', 'hour', 'minute', 'second'))
    # convert month to an int in the range 1..12
    m['month'] = (month_.index(m['month']) - 9) // 4 + 1
    # ensure year is 4 digits; assume everything in the 90's is the 1990's
    if m['year'] < 100:
        m['year'] += (1900, 2000)[m['year'] < 90]
    if m['tz'][0] in '+-':
        tzhour, tzmin = int(m['tz'][1:-2]), int(m['tz'][-2:])
        tzhour, tzmin = [(-2 * (m['tz'][0] == '-') + 1) * x for x in (tzhour, tzmin)]
        delta = datetime.timedelta(0,0,0,0, tzmin, tzhour)
    else:
        tzinfo = {
                 ('ut','gmt','z'): 0,
                 ('edt',): -4,
                 ('est','cdt'): -5,
                 ('cst','mdt'): -6,
                 ('mst','pdt'): -7,
                 ('pst',): -8,
                 ('a',): -1,
                 ('n',): 1,
                 ('m',): -12,
                 ('y',): 12,
                 }
        tzhour = (v for k, v in tzinfo.items() if m['tz'] in k).next()
        delta = datetime.timedelta(0,0,0,0,0, tzhour)
    stamp = datetime.datetime(*[m[x] for x in ('year','month','day','hour','minute','second')])
    return stamp - delta
