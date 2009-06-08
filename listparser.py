# listparser.py - Parse OPML feed lists into a negotiable format.
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
import BeautifulSoup

def parse(filename_or_url):
    try:
        f = urllib2.urlopen(filename_or_url)
    except:
        return {}
    soup = BeautifulSoup.BeautifulSoup(f)
    f.close()

    if soup.opml:
       return _parse_opml(soup)

    return {}

def _parse_opml(soup):
    lst = {
        'meta': {},
        'feeds': [],
    }

    # Collect the list's metadata
    if soup.opml.head:
        if soup.opml.head.title:
            lst['meta']['title'] = soup.opml.head.title.string
        if soup.opml.head.ownername:
            lst['meta'].setdefault('author', {})['name'] = soup.opml.head.ownername.string
        if soup.opml.head.owneremail:
            lst['meta'].setdefault('author', {})['email'] = soup.opml.head.owneremail.string
        if soup.opml.head.ownerid:
            lst['meta'].setdefault('author', {})['url'] = soup.opml.head.ownerid.string

    # When repeated, attributes listed first have lower precedence than those listed last
    opml_mapping = (
        ('url', 'xmlurl'),
        # Feed name (prefer 'text' to 'title')
        ('name', 'title'),
        ('name', 'text'),
    )
    # Collect all available Feeds in the OPML document
    for outline in soup.findAll('outline', attrs = {'type': ('rss', 'pie'), 'xmlurl': True}):
        feed = {}
        for mapping in opml_mapping:
            if outline.has_key(mapping[1]):
                feed[mapping[0]] = outline[mapping[1]]
        lst['feeds'].append(feed)

    return lst
