# This file is part of listparser.
# Copyright 2009-2021 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import datetime  # noqa: F401 (required by evals)
import pathlib

import pytest

import listparser


tests_path = pathlib.Path(__file__).parent


def test_image():
    path = tests_path / '1x1.gif'
    result = listparser.parse(str(path))
    assert result.bozo


def test_return_guarantees():
    result = listparser.parse(0)
    assert result.bozo


empty_doc = '<?xml version="1.0"?><opml />'


@pytest.mark.parametrize('src', [
    empty_doc,  # str
    empty_doc.encode('utf8'),  # bytes
])
def test_get_content_good(src):
    content, info = listparser.get_content(src)
    assert content is not None
    assert not info['bozo']


def test_get_content_bad():
    content, info = listparser.get_content(123)
    assert content is None
    assert info['bozo']


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
    idoc = listparser.Injector(doc)
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
    assert result.feeds[0].title == 'á'  # &aacute;


tests = []
for _file in tests_path.rglob('**/*.xml'):
    _info = {}
    _assertions = []
    blob = _file.read_text('utf8', errors='replace')
    for _line in blob.splitlines():  # pragma: no branch
        if '-->' in _line:
            break
        if _line.lstrip().startswith('Eval:'):
            _assertions.append(_line.partition(':')[2].strip())
        elif ': ' in _line:
            _key, _, _value = _line.strip().partition(': ')
            _info[_key] = _value
    description = _info.get('Description', '')

    if not description:  # pragma: no cover
        message = 'Description not found in test {}'.format(_file)
        raise ValueError(message)
    if not _assertions:  # pragma: no cover
        message = 'Eval not found in test {}'.format(_file)
        raise ValueError(message)

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
