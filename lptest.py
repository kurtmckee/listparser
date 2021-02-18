# This file is part of listparser.
# Copyright 2009-2021 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import datetime  # noqa: F401 (required by evals)
import io
import os
import pathlib
import threading

import pytest
import http.server

try:
    import requests
except ImportError:
    requests = None

import listparser.dates


def test_image():
    path = os.path.abspath(os.path.join('tests', '1x1.gif'))
    result = listparser.parse(path)
    assert result.bozo


def test_return_guarantees():
    result = listparser.parse(0)
    assert result.bozo


empty_doc = '<?xml version="1.0"?><opml />'
testfile = os.path.join('tests', 'filename.xml')


@pytest.mark.parametrize('obj', [
    empty_doc,  # str
    empty_doc.encode('utf8'),  # bytes
])
def test_get_content_good(obj):
    content, info = listparser.get_content(obj)
    assert content is not None
    assert not info


@pytest.mark.parametrize(
    'src',
    [
        True,  # unparsable object
        'http://',  # URL unreachable
    ],
)
def test_get_content_bad(src):
    content, info = listparser.get_content(src)
    assert content is None
    assert info.bozo == 1


@pytest.fixture(params=[1, 20])
def injector_fixture(request):
    size = request.param
    doc = b"""<?xml version="1.0"?><rdf:RDF
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:foaf="http://xmlns.com/foaf/0.1/"
            xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
            xmlns:rss="http://purl.org/rss/1.0/">
            <foaf:Agent><foaf:name>&aacute;</foaf:name><foaf:weblog>
            <foaf:Document rdf:about="http://domain/"><rdfs:seeAlso>
            <rss:channel rdf:about="http://domain/feed" />
            </rdfs:seeAlso></foaf:Document></foaf:weblog></foaf:Agent>
            </rdf:RDF>"""
    idoc = listparser.Injector(io.BytesIO(doc))
    tmp = []
    while 1:
        i = idoc.read(size)
        if i:
            tmp.append(i)
        else:
            idoc.close()
            break
    return b''.join(tmp).decode('utf8')


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
    result = listparser.dates.rfc822(date)
    for key, expected_value in zip(keys, expected_values):
        assert getattr(result, key) == expected_value


@pytest.mark.parametrize('date,expected_year', [
    ('Wed, 21 Jun 00 12:00:00 GMT', 2000),
    ('Wed, 21 Jun 89 12:00:00 GMT', 2089),
    ('Thu, 21 Jun 90 12:00:00 GMT', 1990),
    ('Mon, 21 Jun 99 12:00:00 GMT', 1999),
])
def test_two_digit_years(date, expected_year):
    assert listparser.dates.rfc822(date).year == expected_year


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
    assert listparser.dates.rfc822(date).month == expected_month


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
    result = listparser.dates.rfc822(date)
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
    assert listparser.dates.rfc822(date) is None


tests_path = pathlib.Path(__file__).parent / 'tests/'
_http_test_count = 0
tests = []
for _file in tests_path.rglob('**/*.xml'):
    _info = {}
    _assertions = []
    blob = _file.read_bytes()
    for _line in blob.decode('utf8', errors='replace').splitlines():
        if '-->' in _line:
            break
        if _line.lstrip().startswith('Eval:'):
            _assertions.append(_line.partition(':')[2].strip())
        elif ': ' in _line:
            _key, _, _value = _line.strip().partition(': ')
            _info[_key] = _value
    description = _info.get('Description', '')
    if 'http' in str(_file):
        _http_test_count += int(_info.get('Requests', 1))

    if 'No-Eval' in _info:
        # No-Eval files are requested over HTTP (generally representing
        # an HTTP redirection destination) and contain no testcases.
        # They probably have a Requests directive, though, which is why
        # the `continue` here appears after http_test_count is incremented.
        continue

    if not description:  # pragma: no cover
        message = 'Description not found in test {}'.format(testfile)
        raise ValueError(message)
    if not _assertions:  # pragma: no cover
        message = 'Eval not found in test {}'.format(testfile)
        raise ValueError(message)

    if 'http' in str(_file):
        _path = str(_file.relative_to(tests_path)).replace('\\', '/')
        _src = 'http://localhost:8091/tests/' + _path
        if requests:
            tests.append(pytest.param(
                _src, _assertions,
                id=str(_file.relative_to(tests_path)),
            ))
        else:
            tests.append(pytest.param(
                _src, _assertions,
                id=str(_file.relative_to(tests_path)),
                marks=pytest.mark.xfail,
            ))
    else:
        tests.append(pytest.param(
            blob, _assertions,
            id=str(_file.relative_to(tests_path)),
        ))


@pytest.mark.parametrize('src, assertions', tests)
def test_file(src, assertions):
    # `result` must exist in the local scope for the assertions to run.
    result = listparser.parse(src)  # noqa: F841
    for assertion in assertions:
        assert eval(assertion)


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        status = 200
        location = None
        end_directives = False
        filename = os.path.dirname(os.path.abspath(__file__)) + self.path
        with open(filename, 'rb') as f:
            reply = f.read()
        for line in reply.decode('utf8', 'replace').splitlines():
            if not end_directives:
                if line.strip() == '-->':
                    end_directives = True
                elif 'Status:' in line:
                    status = int(line.strip()[7:])
                elif 'Location:' in line:
                    location = line.strip()[9:].strip()
        self.send_response(status)
        if location:
            self.send_header('Location', location)
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
        httpd = http.server.HTTPServer(('127.0.0.1', 8091), Handler)
        self.ready.set()
        for i in range(self.http_test_count):
            httpd.handle_request()


if requests is not None:
    server = ServerThread(_http_test_count)
    server.daemon = True
    server.start()

    # Wait for the server thread to signal that it's ready
    server.ready.wait()
