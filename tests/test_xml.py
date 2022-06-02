# This file is part of listparser.
# Copyright 2009-2022 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import datetime  # noqa: F401 (required by evals)
import pathlib
import unittest.mock

import pytest

import listparser


tests_path = pathlib.Path(__file__).parent


@pytest.fixture(scope='module')
def use_dict():
    with unittest.mock.patch('listparser.common.SuperDict', dict):
        yield


def test_return_guarantees(use_dict):
    result = listparser.parse(0)
    assert result['bozo']


empty_doc = '<?xml version="1.0"?><opml />'


@pytest.mark.parametrize('src', [
    empty_doc,  # str
    empty_doc.encode('utf8'),  # bytes
])
def test_get_content_good(use_dict, src):
    content, info = listparser.get_content(src)
    assert content is not None
    assert not info['bozo']


def test_get_content_bad(use_dict):
    content, info = listparser.get_content(123)
    assert content is None
    assert info['bozo']


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
def test_file(use_dict, src, assertions):
    # `result` must exist in the local scope for the assertions to run.
    result = listparser.parse(src)  # noqa: F841
    lxml = listparser.parsers.lxml  # noqa: F841
    for assertion in assertions:
        assert eval(assertion)
