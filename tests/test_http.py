# This file is part of listparser.
# Copyright 2009-2022 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import unittest.mock

import pytest

import listparser

try:
    import requests
except ImportError:
    requests = None


empty_doc = '<?xml version="1.0"?><opml />'


@pytest.fixture
def http():
    def get(url, *args, **kwargs):
        if url == 'http://':
            raise requests.exceptions.InvalidURL('no host supplied')
        else:
            mock = unittest.mock.Mock()
            mock.text = empty_doc
            return mock

    with unittest.mock.patch('listparser.requests.get', get):
        yield


@pytest.mark.skipif(requests is None, reason='requests must be installed')
def test_requests_success(http):
    content, info = listparser.get_content('http://example')
    assert content
    assert not info['bozo']


@pytest.mark.skipif(requests is None, reason='requests must be installed')
def test_requests_error(http):
    content, info = listparser.get_content('http://')
    assert not content
    assert info['bozo']


@pytest.mark.skipif(requests, reason='requests must NOT be installed')
def test_requests_not_present():
    content, info = listparser.get_content('http://example')
    assert not content
    assert info['bozo']
    assert isinstance(info['bozo_exception'], listparser.ListparserError)
