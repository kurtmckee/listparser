# lptest.py - Run unit tests against listparser.py
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

import os
from os.path import abspath, dirname, join, splitext
import threading
import unittest
import BaseHTTPServer
import SimpleHTTPServer
import StringIO

import listparser

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        status = 200
        location = u''
        reply = u''
        end_directives = False
        f = open(dirname(abspath(__file__)) + self.path, 'r')
        for line in f:
            reply += line
            if not end_directives:
                if line.strip() == '-->':
                    end_directives = True
                elif 'Status:' in line:
                    status = int(line.strip()[7:])
                elif 'Location:' in line:
                    location = line.strip()[9:].strip()
                elif 'ETag:' in line:
                    etag = line.strip()[5:].strip()
                    if self.headers['if-none-match'] == etag:
                        status = 304
                elif 'Modified:' in line:
                    modified = line.strip()[10:].strip()
                    if self.headers['if-modified-since'] == modified:
                        status = 304
        f.close()
        self.send_response(status)
        if location:
            self.send_header('Location', location)
        self.send_header('Content-type', 'text/xml')
        self.end_headers()
        self.wfile.write(reply)
    def log_request(self, *arg, **karg):
        pass

class ServerThread(threading.Thread):
    def __init__(self, numtests):
        super(ServerThread, self).__init__()
        self.numtests = numtests
    def run(self):
        server = BaseHTTPServer.HTTPServer
        bind_to = ('', 8091)
        reqhandler = Handler
        httpd = server(bind_to, reqhandler)
        while self.numtests:
            httpd.handle_request()
            self.numtests -= 1

class TestCases(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testStringInput(self):
        t = """<?xml version="1.0"?><opml version="2.0"><head><title>
        String Input Test</title></head><body><outline text="node" />
        </body></opml>"""
        result = listparser.parse(t)
        self.assert_(result['bozo'] == 0)
        self.assert_(result['meta']['title'] == u'String Input Test')
    def testFileishInput(self):
        t = """<?xml version="1.0"?><opml version="2.0"><head><title>
        Fileish Input Test</title></head><body><outline text="node" />
        </body></opml>"""
        result = listparser.parse(StringIO.StringIO(t))
        self.assert_(result['bozo'] == 0)
        self.assert_(result['meta']['title'] == u'Fileish Input Test')
    def worker(self, evals, testfile, etag, modified):
        result = listparser.parse('http://localhost:8091/tests/' + testfile,
            etag=etag, modified=modified)
        map(self.assert_, map(eval, evals))

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
    if 'http/destination' in testfile:
        # destination.xml is the target of four redirect requests
        numtests += 4
        continue
    numtests += 1
    description = ''
    etag = modified = None
    evals = []
    openfile = open(join(testpath, testfile))
    for line in openfile:
        line = line.strip()
        if '-->' in line:
            break
        if 'Description:' in line:
            description = line.split('Description:')[1].strip()
        if 'Eval:' in line:
            evals.append(line.split('Eval:')[1].strip())
        if 'ETag:' in line:
            etag = line.strip()[5:].strip()
        if 'Modified:' in line:
            modified = line.strip()[9:].strip()
    openfile.close()
    if not description:
        raise ValueError("Description not found in test %s" % testfile)
    if not evals:
        raise ValueError("Eval not found in test %s" % testfile)
    testcase = make_testcase(evals, testfile, etag, modified)
    testcase.__doc__ = '%s: %s' % (testfile, description)
    setattr(TestCases, 'test_%s' % splitext(testfile)[0], testcase)

server = ServerThread(numtests)
server.start()

testsuite = unittest.TestLoader().loadTestsFromTestCase(TestCases)
unittest.TextTestRunner(verbosity=1).run(testsuite)
