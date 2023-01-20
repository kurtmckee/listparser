# This file is part of listparser.
# Copyright 2009-2023 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import pytest

from listparser.common import SuperDict


def test_attr_get():
    sample = SuperDict()
    dict.__setitem__(sample, "a", 1)
    assert sample.a == 1


def test_attr_get_error():
    with pytest.raises(AttributeError):
        assert SuperDict().bogus
