# lptest.py - Run unit tests against listparser.py
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

import datetime  # noqa: F401 (required by evals)
import os
import threading

import pytest

import listparser.dates

try:
    # Python 2
    import BaseHTTPServer
    import SimpleHTTPServer
except ImportError:
    # Python 3
    import http.server
    BaseHTTPServer = http.server
    SimpleHTTPServer = http.server

try:
    # Python 2
    from StringIO import StringIO
except ImportError:
    # Python 3
    from io import StringIO

try:
    if bytes is str:
        # bytes is an alias for str in Python 2.6 and 2.7
        raise NameError
except NameError:
    # Python 2
    def _to_unicode(obj):
        """_to_unicode(str or unicode) -> unicode"""
        if isinstance(obj, str):
            obj.decode('utf-8')
        return obj
else:
    # Python 3
    def _to_unicode(obj):
        """_to_unicode(bytes or str) -> str"""
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return obj

try:
    unicode
except NameError:
    # Python 3
    def _to_str(obj):
        return obj
else:
    # Python 2
    def _to_str(obj):
        """_to_str(unicode or str) -> str (UTF-8 encoded)"""
        if isinstance(obj, unicode):  # noqa: F821
            return obj.encode('utf-8')
        return obj


def test_useragent_invalid():
    url = 'http://localhost:8091/tests/http/useragent.xml'
    obj, sdict = listparser._mkfile(url, True, None, None)
    obj.close()
    assert sdict.status == 200


def test_useragent_default():
    url = 'http://localhost:8091/tests/http/useragent.xml'
    result = listparser.parse(url)
    assert not result.bozo
    assert result.headers.get('x-agent') == listparser.USER_AGENT


def test_useragent_custom():
    url = 'http://localhost:8091/tests/http/useragent.xml'
    result = listparser.parse(url, agent="CustomAgent")
    assert not result.bozo
    assert result.headers.get('x-agent') == "CustomAgent"


def test_useragent_global_override():
    url = 'http://localhost:8091/tests/http/useragent.xml'
    tmp = listparser.USER_AGENT
    listparser.USER_AGENT = "NewGlobalAgent"
    result = listparser.parse(url)
    listparser.USER_AGENT = tmp
    assert not result.bozo
    assert result.headers.get('x-agent') == "NewGlobalAgent"


def test_image():
    path = os.path.abspath(os.path.join('tests', '1x1.gif'))
    result = listparser.parse(path)
    assert result.bozo


doc = """<?xml version="1.0"?><opml />"""
testfile = os.path.join('tests', 'filename.xml')


@pytest.mark.parametrize('obj', [
    doc,  # string input
    StringIO(_to_str(doc)),  # file-like object
    testfile,  # relative path
    os.path.abspath(testfile),  # absolute path
])
def test_good_mkfile(obj):
    f, sdict = listparser._mkfile(obj, 'agent', None, None)
    f.close()
    assert f is not None
    assert not sdict


@pytest.mark.parametrize('obj', [
    True,  # unparsable object
    "xxx://badurl.com/",  # bad protocol
    "http://badurl.com.INVALID/",  # URL unreachable
    'totally made up and bogus /\:',  # bogus filename
])
def test_bad_mkfile(obj):
    n, sdict = listparser._mkfile(obj, 'agent', None, None)
    assert n is None
    assert sdict.bozo == 1


@pytest.fixture(params=[1, 20])
def injector_fixture(request):
    size = request.param
    doc = listparser._to_bytes("""<?xml version="1.0"?><rdf:RDF
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:foaf="http://xmlns.com/foaf/0.1/"
            xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
            xmlns:rss="http://purl.org/rss/1.0/">
            <foaf:Agent><foaf:name>&aacute;</foaf:name><foaf:weblog>
            <foaf:Document rdf:about="http://domain/"><rdfs:seeAlso>
            <rss:channel rdf:about="http://domain/feed" />
            </rdfs:seeAlso></foaf:Document></foaf:weblog></foaf:Agent>
            </rdf:RDF>""")
    idoc = listparser.Injector(listparser.BytesStrIO(doc))
    tmp = []
    while 1:
        i = idoc.read(size)
        if i:
            tmp.append(i)
        else:
            idoc.close()
            break
    return _to_unicode(listparser._to_bytes('').join(tmp))


def test_injector(injector_fixture):
    result = listparser.parse(injector_fixture)
    assert not result.bozo
    assert len(result.feeds) == 1
    assert ord(result.feeds[0].title) == 225  # \u00e1


@pytest.mark.parametrize('date,expected_values', [
    ('Sun, 14 Jun 2009 11:47:32 GMT', (2009, 6, 14, 11, 47, 32)),
    ('Sun, Dec 16 2012 11:15:01 GMT', (2012, 12, 16, 11, 15, 1)),
    ('Sun, Dec 16 2012', (2012, 12, 16, 0, 0, 0)),
    ('Thu,  5 Apr 2012 10:00:00 GMT', (2012, 4, 5, 10, 0, 0)),
    ('Sun, 21 Jun 2009 12:00 GMT', (2009, 6, 21, 12, 0, 0)),
])
def test_format_variations(date, expected_values):
    keys = ('year', 'month', 'day', 'hour', 'minute', 'second')
    result = listparser.dates._rfc822(date)
    for key, expected_value in zip(keys, expected_values):
        assert getattr(result, key) == expected_value


@pytest.mark.parametrize('date,expected_year', [
    ('Wed, 21 Jun 00 12:00:00 GMT', 2000),
    ('Wed, 21 Jun 89 12:00:00 GMT', 2089),
    ('Thu, 21 Jun 90 12:00:00 GMT', 1990),
    ('Mon, 21 Jun 99 12:00:00 GMT', 1999),
])
def test_two_digit_years(date, expected_year):
    assert listparser.dates._rfc822(date).year == expected_year


@pytest.mark.parametrize('date,expected_month', [
    ('21 Jan 2009 12:00:00 GMT', 1),
    ('21 Feb 2009 12:00:00 GMT', 2),
    ('21 Mar 2009 12:00:00 GMT', 3),
    ('21 Apr 2009 12:00:00 GMT', 4),
    ('21 May 2009 12:00:00 GMT', 5),
    ('21 Jun 2009 12:00:00 GMT', 6),
    ('21 Jul 2009 12:00:00 GMT', 7),
    ('21 Aug 2009 12:00:00 GMT', 8),
    ('21 Sep 2009 12:00:00 GMT', 9),
    ('21 Oct 2009 12:00:00 GMT', 10),
    ('21 Nov 2009 12:00:00 GMT', 11),
    ('21 Dec 2009 12:00:00 GMT', 12),
])
def test_month_names(date, expected_month):
    assert listparser.dates._rfc822(date).month == expected_month


@pytest.mark.parametrize('date,hour,minute,day', [
    ('Mon, 22 Jun 2009 13:15:17 Z', 13, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 UT', 13, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 GMT', 13, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 CDT', 18, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 CST', 19, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 EDT', 17, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 EST', 18, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 MDT', 19, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 MST', 20, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 PDT', 20, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 PST', 21, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 A', 14, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 N', 12, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 M', 1, 15, 23),
    ('Mon, 22 Jun 2009 13:15:17 Y', 1, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 -0430', 17, 45, 22),
    ('Mon, 22 Jun 2009 13:15:17 +0545', 7, 30, 22),
    ('Mon, 22 Jun 2009 13:15:17 Etc/GMT', 13, 15, 22),
    ('Mon, 22 Jun 2009 13:15:17 Etc/', 13, 15, 22),
])
def test_timezones(date, hour, minute, day):
    result = listparser.dates._rfc822(date)
    assert result.hour == hour
    assert result.minute == minute
    assert result.day == day


@pytest.mark.parametrize('date', [
    'Sun, 99 Jun 2009 12:00:00 GMT',  # range day high
    'Sun, 00 Jun 2009 12:00:00 GMT',  # range day low
    'Sun, 01 Jun 2009 99:00:00 GMT',  # range hour
    'Sun, 01 Jun 2009 00:99:00 GMT',  # range minute
    'Sun, 01 Jun 2009 00:00:99 GMT',  # range second
    'Sun, 31 Dec 9999 23:59:59 -9999',  # range year high
    'Sun, 01 Jan 0000 00:00:00 +9999',  # range year low
    'yesterday',  # too few parts
    'Sun, 16 Dec 2012 1:2:3:4 GMT',  # too many time parts
    'Sun, 16 zzz 2012 11:47:32 GMT',  # bad month name
    'Sun, Dec x 2012 11:47:32 GMT',  # bad month/day swap
    'Sun, 16 Dec zz 11:47:32 GMT',  # bad year
    'Sun, 16 Dec 2012 11:47:32 +zz:00',  # bad positive timezone hour
    'Sun, 16 Dec 2012 11:47:32 +00:zz',  # bad positive timezone minute
    'Sun, 16 Dec 2012 11:47:32 -zz:00',  # bad negative timezone hour
    'Sun, 16 Dec 2012 11:47:32 -00:zz',  # bad negative timezone minute
])
def test_invalid_dates(date):
    assert listparser.dates._rfc822(date) is None


http_test_count = 0
tests = []
tests_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests/')
filenames = (
    os.path.join(root, filename).replace(tests_path, '', 1)
    for root, directories, files in os.walk(tests_path)
    for filename in files
    if filename.endswith('.xml')
)
for filename in filenames:
    info = {}
    assertions = []
    with open(os.path.join('tests', filename), 'rb') as f:
        blob = f.read()
    for line in blob.splitlines():
        line = line.decode('utf8', 'replace').strip()
        if '-->' in line:
            break
        if line.lstrip().startswith('Eval:'):
            assertions.append(line.split(': ', 1)[1].strip())
        elif ': ' in line:
            info.update((map(str.strip, _to_str(line).split(': ', 1)),))
    description = info.get('Description', '')
    etag = info.get('ETag', None)
    modified = info.get('Modified', None)
    if 'http' in filename:
        http_test_count += int(info.get('Requests', 1))

    if 'No-Eval' in info:
        # No-Eval files are requested over HTTP (generally representing
        # an HTTP redirection destination) and contain no testcases.
        # They probably have a Requests directive, though, which is why
        # the `continue` here appears after http_test_count is incremented.
        continue

    if not description:
        message = 'Description not found in test {}'.format(testfile)
        raise ValueError(message)
    if not assertions:
        message = 'Eval not found in test {}'.format(testfile)
        raise ValueError(message)

    tests.append([filename, etag, modified, assertions])
    if modified:
        # Create a datetime test for `modified`.
        modified = listparser.dates._rfc822(modified)
        tests.append([filename, etag, modified, assertions])


@pytest.mark.parametrize('filename,etag,modified,assertions', tests)
def test_file(filename, etag, modified, assertions):
    if 'http' in filename:
        path = 'http://localhost:8091/tests/' + filename
    else:
        path = os.path.join('tests', filename)
    # `result` must exist in the local scope for the assertions to run.
    result = listparser.parse(path, etag=etag, modified=modified)  # noqa: F841
    for assertion in assertions:
        assert eval(assertion)


class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        status = 200
        location = etag = modified = None
        reply = listparser._to_bytes('')
        end_directives = False
        f = open(os.path.dirname(os.path.abspath(__file__)) + self.path, 'rb')
        for line in f:
            reply += line
            line = line.decode('utf8', 'replace')
            if not end_directives:
                if line.strip() == '-->':
                    end_directives = True
                elif 'Status:' in line:
                    status = int(line.strip()[7:])
                elif 'Location:' in line:
                    location = line.strip()[9:].strip()
                elif 'Server-ETag:' in line:
                    etag = line.split(': ', 1)[1].strip()
                    if self.headers.get('if-none-match') == etag:
                        status = 304
                elif 'Server-Modified:' in line:
                    modified = line.split(': ', 1)[1].strip()
                    if self.headers.get('if-modified-since') == modified:
                        status = 304
        f.close()
        self.send_response(status)
        if location:
            self.send_header('Location', location)
        if etag:
            self.send_header('ETag', etag)
        if modified:
            self.send_header('Last-Modified', modified)
        self.send_header('Content-type', 'text/xml')
        self.send_header('x-agent', self.headers.get('user-agent'))
        self.end_headers()
        self.wfile.write(reply)

    def log_request(self, *arg, **karg):
        pass


class ServerThread(threading.Thread):
    def __init__(self, http_test_count):
        super(ServerThread, self).__init__()
        self.http_test_count = http_test_count
        self.ready = threading.Event()

    def run(self):
        server = BaseHTTPServer.HTTPServer
        bind_to = ('127.0.0.1', 8091)
        reqhandler = Handler
        httpd = server(bind_to, reqhandler)
        self.ready.set()
        for i in range(self.http_test_count):
            httpd.handle_request()


server = ServerThread(http_test_count)
server.daemon = True
server.start()

# Wait for the server thread to signal that it's ready
server.ready.wait()
