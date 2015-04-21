# lptest.py - Run unit tests against listparser.py
# Copyright (C) 2009-2015 Kurt McKee <contactme@kurtmckee.org>
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

import datetime # required by evals
import os
from os.path import abspath, dirname, join, splitext
import threading
import unittest
import sys

import listparser

try:
    import BaseHTTPServer
    import SimpleHTTPServer
except ImportError:
    import http.server
    BaseHTTPServer = http.server
    SimpleHTTPServer = http.server

try:
    from StringIO import StringIO
except ImportError:
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
        if isinstance(obj, unicode):
            return obj.encode('utf-8')
        return obj

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        status = 200
        location = etag = modified = None
        reply = listparser._to_bytes('')
        end_directives = False
        f = open(dirname(abspath(__file__)) + self.path, 'rb')
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
    def __init__(self, numtests):
        super(ServerThread, self).__init__()
        self.numtests = numtests
        self.ready = threading.Event()
    def run(self):
        server = BaseHTTPServer.HTTPServer
        bind_to = ('127.0.0.1', 8091)
        reqhandler = Handler
        httpd = server(bind_to, reqhandler)
        self.ready.set()
        for i in range(self.numtests):
            httpd.handle_request()

class TestCases(unittest.TestCase):
    def testUserAgentInvalid(self):
        url = 'http://localhost:8091/tests/http/useragent.xml'
        obj, sdict = listparser._mkfile(url, True, None, None)
        obj.close()
        self.assertEqual(sdict.status, 200)
    def testUserAgentDefault(self):
        url = 'http://localhost:8091/tests/http/useragent.xml'
        result = listparser.parse(url)
        self.assertFalse(result.bozo)
        self.assert_(result.headers.get('x-agent') == listparser.USER_AGENT)
    def testUserAgentCustomArg(self):
        url = 'http://localhost:8091/tests/http/useragent.xml'
        result = listparser.parse(url, agent="CustomAgent")
        self.assertFalse(result.bozo)
        self.assert_(result.headers.get('x-agent') == "CustomAgent")
    def testUserAgentGlobalOverride(self):
        url = 'http://localhost:8091/tests/http/useragent.xml'
        tmp = listparser.USER_AGENT
        listparser.USER_AGENT = "NewGlobalAgent"
        result = listparser.parse(url)
        listparser.USER_AGENT = tmp
        self.assertFalse(result.bozo)
        self.assert_(result.headers.get('x-agent') == "NewGlobalAgent")
    def testImage(self):
        f = os.path.abspath(os.path.join('tests', '1x1.gif'))
        result = listparser.parse(f)
        self.assert_(result.bozo == 1)
    def worker(self, evals, testfile, etag, modified):
        if 'http' in testfile:
            testfile = 'http://localhost:8091/tests/' + testfile
        else:
            testfile = join('tests', testfile)
        result = listparser.parse(testfile, etag=etag, modified=modified)
        for ev in evals:
            self.assert_(eval(ev))

class TestMkfile(unittest.TestCase):
    def _bad_test(obj):
        # A TestCase factory; its tests assume unusable return values
        def fn(self):
            n, sdict = listparser._mkfile(obj, 'agent', None, None)
            self.assert_(n is None)
            self.assertEqual(sdict.bozo, 1)
        return fn
    testUnparsableObject = _bad_test(True)
    testBadURLProtocol = _bad_test("xxx://badurl.com/")
    testBadURLUnreachable = _bad_test("http://badurl.com.INVALID/")
    testBogusFilename = _bad_test('totally made up and bogus /\:')

    def _good_test(obj):
        # A TestCase factory; its tests expect a usable file-like or
        # stream object and an empty SuperDict will be returned
        def fn(self):
            f, sdict = listparser._mkfile(obj, 'agent', None, None)
            f.close()
            self.assert_(f is not None)
            self.assertFalse(sdict)
        return fn
    doc = """<?xml version="1.0"?><opml />"""
    testStringInput = _good_test(doc)
    testFileishInput = _good_test(StringIO(_to_str(doc)))

    testfile = os.path.join('tests', 'filename.xml')
    testRelativeFilename = _good_test(testfile)
    testAbsoluteFilename = _good_test(os.path.abspath(testfile))

class TestInjection(unittest.TestCase):
    def _read_size(size):
        # Return a TestCase function that will manually feed the subscription
        # list through the Injector, calling read() using the given size
        def fn(self):
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
            xml = _to_unicode(listparser._to_bytes('').join(tmp))
            result = listparser.parse(xml)
            self.assertFalse(result.bozo)
            self.assertEqual(len(result.feeds), 1)
            self.assertEqual(ord(result.feeds[0].title), 225) # \u00e1
        return fn
    testRead1by1 = _read_size(1)
    testReadChunks = _read_size(20)

class TestRFC822(unittest.TestCase):
    def testGeneral(self):
        dt = listparser._rfc822('Sun, 14 Jun 2009 11:47:32 GMT')
        self.assertEqual(dt.day, 14)
        self.assertEqual(dt.month, 6)
        self.assertEqual(dt.year, 2009)
        self.assertEqual(dt.hour, 11)
        self.assertEqual(dt.minute, 47)
        self.assertEqual(dt.second, 32)
    def testSwappedMonthAndDay(self):
        dt = listparser._rfc822('Sun, Dec 16 2012 11:15:01 GMT')
        self.assertEqual(dt.day, 16)
        self.assertEqual(dt.month, 12)
        self.assertEqual(dt.year, 2012)
        self.assertEqual(dt.hour, 11)
        self.assertEqual(dt.minute, 15)
        self.assertEqual(dt.second, 1)
    def testMissingTimeAndTimezone(self):
        dt = listparser._rfc822('Sun, Dec 16 2012')
        self.assertEqual(dt.day, 16)
        self.assertEqual(dt.month, 12)
        self.assertEqual(dt.year, 2012)
        self.assertEqual(dt.hour, 0)
        self.assertEqual(dt.minute, 0)
        self.assertEqual(dt.second, 0)
    def testSingleDigitDay(self):
        dt = listparser._rfc822('Thu,  5 Apr 2012 10:00:00 GMT')
        self.assertEqual(dt.day, 5)
    def testSecondMissing(self):
        dt = listparser._rfc822('Sun, 21 Jun 2009 12:00 GMT')
        self.assertEqual(dt.second, 0)

    def _month_test(s, month):
        # Take an RFC822 datetime string and a month integer (1-12) and
        # return a TestCase function that tests that datetime.month == m
        def fn(self):
            dt = listparser._rfc822(s)
            self.assertEqual(dt.month, month)
        return fn
    testMonth01 = _month_test('21 Jan 2009 12:00:00 GMT', 1)
    testMonth02 = _month_test('21 Feb 2009 12:00:00 GMT', 2)
    testMonth03 = _month_test('21 Mar 2009 12:00:00 GMT', 3)
    testMonth04 = _month_test('21 Apr 2009 12:00:00 GMT', 4)
    testMonth05 = _month_test('21 May 2009 12:00:00 GMT', 5)
    testMonth06 = _month_test('21 Jun 2009 12:00:00 GMT', 6)
    testMonth07 = _month_test('21 Jul 2009 12:00:00 GMT', 7)
    testMonth08 = _month_test('21 Aug 2009 12:00:00 GMT', 8)
    testMonth09 = _month_test('21 Sep 2009 12:00:00 GMT', 9)
    testMonth10 = _month_test('21 Oct 2009 12:00:00 GMT', 10)
    testMonth11 = _month_test('21 Nov 2009 12:00:00 GMT', 11)
    testMonth12 = _month_test('21 Dec 2009 12:00:00 GMT', 12)

    def _tz_test(s, hour, minute=15, day=22):
        # Take an RFC822 datetime string, and hour, minute, and day
        # integers, and return a TestCase function that tests that:
        # dt.hour == hour, dt.minute == minute, dt.day == day
        def fn(self):
            dt = listparser._rfc822(s)
            self.assertEqual(dt.hour, hour)
            self.assertEqual(dt.minute, minute)
            self.assertEqual(dt.day, day)
        return fn
    testTZ_Z = _tz_test('Mon, 22 Jun 2009 13:15:17 Z', 13)
    testTZ_UT = _tz_test('Mon, 22 Jun 2009 13:15:17 UT', 13)
    testTZ_GMT = _tz_test('Mon, 22 Jun 2009 13:15:17 GMT', 13)
    testTZ_CDT = _tz_test('Mon, 22 Jun 2009 13:15:17 CDT', 18)
    testTZ_CST = _tz_test('Mon, 22 Jun 2009 13:15:17 CST', 19)
    testTZ_EDT = _tz_test('Mon, 22 Jun 2009 13:15:17 EDT', 17)
    testTZ_EST = _tz_test('Mon, 22 Jun 2009 13:15:17 EST', 18)
    testTZ_MDT = _tz_test('Mon, 22 Jun 2009 13:15:17 MDT', 19)
    testTZ_MST = _tz_test('Mon, 22 Jun 2009 13:15:17 MST', 20)
    testTZ_PDT = _tz_test('Mon, 22 Jun 2009 13:15:17 PDT', 20)
    testTZ_PST = _tz_test('Mon, 22 Jun 2009 13:15:17 PST', 21)
    testTZ_A = _tz_test('Mon, 22 Jun 2009 13:15:17 A', 14)
    testTZ_N = _tz_test('Mon, 22 Jun 2009 13:15:17 N', 12)
    testTZ_M = _tz_test('Mon, 22 Jun 2009 13:15:17 M', 1, day=23)
    testTZ_Y = _tz_test('Mon, 22 Jun 2009 13:15:17 Y', 1, day=22)
    testTZ_plus = _tz_test('Mon, 22 Jun 2009 13:15:17 -0430', 17, minute=45)
    testTZ_minus = _tz_test('Mon, 22 Jun 2009 13:15:17 +0545', 7, minute=30)
    testTZ_ETC_GMT = _tz_test('Mon, 22 Jun 2009 13:15:17 Etc/GMT', 13)
    testTZ_crasher = _tz_test('Mon, 22 Jun 2009 13:15:17 Etc/', 13)

    def _year2digit_test(s, year):
        # Take an RFC822 datetime string and a year and,
        # return a TestCase that tests that dt.year == y
        def fn(self):
            dt = listparser._rfc822(s)
            self.assertEqual(dt.year, year)
        return fn
    testYear2Digit00 = _year2digit_test('Wed, 21 Jun 00 12:00:00 GMT', 2000)
    testYear2Digit89 = _year2digit_test('Wed, 21 Jun 89 12:00:00 GMT', 2089)
    testYear2Digit90 = _year2digit_test('Thu, 21 Jun 90 12:00:00 GMT', 1990)
    testYear2Digit99 = _year2digit_test('Mon, 21 Jun 99 12:00:00 GMT', 1999)

    def _invalid_date_test(s):
        # Test extreme date and time ranges
        def fn(self):
            dt = listparser._rfc822(s)
            self.assertEqual(dt, None)
        return fn
    testRangeDayHigh = _invalid_date_test('Sun, 99 Jun 2009 12:00:00 GMT')
    testRangeDayLow = _invalid_date_test('Sun, 00 Jun 2009 12:00:00 GMT')
    testRangeHour = _invalid_date_test('Sun, 01 Jun 2009 99:00:00 GMT')
    testRangeMinute = _invalid_date_test('Sun, 01 Jun 2009 00:99:00 GMT')
    testRangeSecond = _invalid_date_test('Sun, 01 Jun 2009 00:00:99 GMT')
    testRangeYearHigh = _invalid_date_test('Sun, 31 Dec 9999 23:59:59 -9999')
    testRangeYearLow = _invalid_date_test('Sun, 01 Jan 0000 00:00:00 +9999')
    testTooFewParts = _invalid_date_test('yesterday')
    testTooManyTimeParts = _invalid_date_test('Sun, 16 Dec 2012 1:2:3:4 GMT')
    testBadMonthName = _invalid_date_test('Sun, 16 zzz 2012 11:47:32 GMT')
    testBadMonthDaySwap = _invalid_date_test('Sun, Dec x 2012 11:47:32 GMT')
    testBadYear = _invalid_date_test('Sun, 16 Dec zz 11:47:32 GMT')
    testBadPosTZHour = _invalid_date_test('Sun, 16 Dec 2012 11:47:32 +zz:00')
    testBadPosTZMinute = _invalid_date_test('Sun, 16 Dec 2012 11:47:32 +00:zz')
    testBadNegTZHour = _invalid_date_test('Sun, 16 Dec 2012 11:47:32 -zz:00')
    testBadNegTZMinute = _invalid_date_test('Sun, 16 Dec 2012 11:47:32 -00:zz')

def make_testcase(evals, testfile, etag, modified):
    # HACK: Only necessary in order to ensure that `evals` is evaluated
    # for every testcase, not just for the last one in the loop below
    # (where, apparently, `lambda` would cause it to be evaluated only
    # once at the end of the loop, containing the final testcase' values).
    return lambda self: self.worker(evals, testfile, etag, modified)

numtests = 0
testpath = join(dirname(abspath(__file__)), 'tests/')
# files contains a list of relative paths to test files
# HACK: replace() is only being used because os.path.relpath()
# was only added to Python in version 2.6
files = (join(r, f).replace(testpath, '', 1)
            for r, d, files in os.walk(testpath)
            for f in files if f.endswith('.xml'))
for testfile in files:
    info = {}
    evals = []
    openfile = open(join(testpath, testfile), 'rb')
    for line in openfile:
        line = line.decode('utf8', 'replace').strip()
        if '-->' in line:
            break
        if line.lstrip().startswith('Eval:'):
            evals.append(line.split(': ', 1)[1].strip())
        elif ': ' in line:
            info.update((map(str.strip, _to_str(line).split(': ', 1)),))
    openfile.close()
    description = info.get('Description', '')
    etag = info.get('ETag', None)
    modified = info.get('Modified', None)
    if 'http' in testfile:
        numtests += int(info.get('Requests', 1))

    if 'No-Eval' in info:
        # No-Eval files are requested over HTTP (generally representing
        # an HTTP redirection destination) and contain no testcases.
        # They probably have a Requests directive, though, which is why
        # the `continue` here appears after numtests is incremented.
        continue
    if not description:
        raise ValueError("Description not found in test %s" % testfile)
    if not evals:
        raise ValueError("Eval not found in test %s" % testfile)
    if modified:
        testcase = make_testcase(evals, testfile, etag, modified)
        testcase.__doc__ = '%s: %s [string]' % (testfile, description)
        setattr(TestCases, 'test_%s_1' % splitext(testfile)[0], testcase)
        testcase = make_testcase(evals, testfile, etag,
                                 listparser._rfc822(modified))
        testcase.__doc__ = '%s: %s [datetime]' % (testfile, description)
        setattr(TestCases, 'test_%s_2' % splitext(testfile)[0], testcase)
    else:
        testcase = make_testcase(evals, testfile, etag, modified)
        testcase.__doc__ = '%s: %s' % (testfile, description)
        setattr(TestCases, 'test_%s' % splitext(testfile)[0], testcase)

server = ServerThread(numtests)
server.setDaemon(True)
server.start()

# Wait for the server thread to signal that it's ready
server.ready.wait()

testsuite = unittest.TestSuite()
testloader = unittest.TestLoader()
testsuite.addTest(testloader.loadTestsFromTestCase(TestCases))
testsuite.addTest(testloader.loadTestsFromTestCase(TestInjection))
testsuite.addTest(testloader.loadTestsFromTestCase(TestRFC822))
testsuite.addTest(testloader.loadTestsFromTestCase(TestMkfile))
testresults = unittest.TextTestRunner(verbosity=1).run(testsuite)

# Return 0 if successful, 1 if there was a failure
sys.exit(not testresults.wasSuccessful())
