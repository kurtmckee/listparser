# This file is part of listparser.
# Copyright 2009-2022 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import datetime

import pytest

import listparser.dates


@pytest.mark.parametrize(
    "date, expected_values",
    [
        ("Sun, 14 Jun 2009 11:47:32 GMT", (2009, 6, 14, 11, 47, 32)),
        ("Sun, Dec 16 2012 11:15:01 GMT", (2012, 12, 16, 11, 15, 1)),
        ("Sun, Dec 16 2012", (2012, 12, 16, 0, 0, 0)),
        ("Thu,  5 Apr 2012 10:00:00 GMT", (2012, 4, 5, 10, 0, 0)),
        ("Sun, 21 Jun 2009 12:00 GMT", (2009, 6, 21, 12, 0, 0)),
    ],
)
def test_format_variations(date, expected_values):
    keys = ("year", "month", "day", "hour", "minute", "second")
    result = listparser.dates.parse_rfc822(date)
    for key, expected_value in zip(keys, expected_values):
        assert getattr(result, key) == expected_value
    assert result.tzinfo == datetime.timezone(datetime.timedelta(0))


@pytest.mark.parametrize(
    "date, expected_year",
    [
        ("Wed, 21 Jun 00 12:00:00 GMT", 2000),
        ("Wed, 21 Jun 89 12:00:00 GMT", 2089),
        ("Thu, 21 Jun 90 12:00:00 GMT", 1990),
        ("Mon, 21 Jun 99 12:00:00 GMT", 1999),
    ],
)
def test_two_digit_years(date, expected_year):
    assert listparser.dates.parse_rfc822(date).year == expected_year


@pytest.mark.parametrize(
    "date, expected_month",
    [
        ("21 Jan 2009 12:00:00 GMT", 1),
        ("21 Feb 2009 12:00:00 GMT", 2),
        ("21 Mar 2009 12:00:00 GMT", 3),
        ("21 Apr 2009 12:00:00 GMT", 4),
        ("21 May 2009 12:00:00 GMT", 5),
        ("21 Jun 2009 12:00:00 GMT", 6),
        ("21 Jul 2009 12:00:00 GMT", 7),
        ("21 Aug 2009 12:00:00 GMT", 8),
        ("21 Sep 2009 12:00:00 GMT", 9),
        ("21 Oct 2009 12:00:00 GMT", 10),
        ("21 Nov 2009 12:00:00 GMT", 11),
        ("21 Dec 2009 12:00:00 GMT", 12),
    ],
)
def test_month_names(date, expected_month):
    assert listparser.dates.parse_rfc822(date).month == expected_month


@pytest.mark.parametrize(
    "date, hour, minute, offset",
    [
        # Universal timezones
        ("Mon, 22 Jun 2009 13:15:17 UT", 13, 15, 0),
        ("Mon, 22 Jun 2009 13:15:17 GMT", 13, 15, 0),
        # North American timezones
        ("Mon, 22 Jun 2009 13:15:17 EST", 13, 15, -5 * 60),
        ("Mon, 22 Jun 2009 13:15:17 EDT", 13, 15, -4 * 60),
        ("Mon, 22 Jun 2009 13:15:17 CST", 13, 15, -6 * 60),
        ("Mon, 22 Jun 2009 13:15:17 CDT", 13, 15, -5 * 60),
        ("Mon, 22 Jun 2009 13:15:17 MST", 13, 15, -7 * 60),
        ("Mon, 22 Jun 2009 13:15:17 MDT", 13, 15, -6 * 60),
        ("Mon, 22 Jun 2009 13:15:17 PST", 13, 15, -8 * 60),
        ("Mon, 22 Jun 2009 13:15:17 PDT", 13, 15, -7 * 60),
        # Military timezones
        ("Mon, 22 Jun 2009 13:15:17 Z", 13, 15, 0),
        ("Mon, 22 Jun 2009 13:15:17 A", 13, 15, -1 * 60),
        ("Mon, 22 Jun 2009 13:15:17 N", 13, 15, +1 * 60),
        ("Mon, 22 Jun 2009 13:15:17 M", 13, 15, -12 * 60),
        ("Mon, 22 Jun 2009 13:15:17 Y", 13, 15, +12 * 60),
        # Numeric timezones
        ("Mon, 22 Jun 2009 13:15:17 -0430", 13, 15, (-4 * 60) - 30),
        ("Mon, 22 Jun 2009 13:15:17 +0545", 13, 15, (5 * 60) + 45),
        ("Mon, 22 Jun 2009 13:15:17 0545", 13, 15, (5 * 60) + 45),
        # Non-standard timezones
        ("Mon, 22 Jun 2009 13:15:17 UTC", 13, 15, 0),
        ("Mon, 22 Jun 2009 13:15:17 Etc/GMT", 13, 15, 0),
        ("Mon, 22 Jun 2009 13:15:17 Etc/", 13, 15, 0),
    ],
)
def test_timezones(date, hour, minute, offset):
    result = listparser.dates.parse_rfc822(date)
    assert result.hour == hour
    assert result.minute == minute
    tz_info = datetime.timezone(datetime.timedelta(minutes=offset))
    assert result.tzinfo == tz_info


@pytest.mark.parametrize(
    "date",
    [
        "Sun, 99 Jun 2009 12:00:00 GMT",  # range day high
        "Sun, 00 Jun 2009 12:00:00 GMT",  # range day low
        "Sun, 01 Jun 2009 99:00:00 GMT",  # range hour
        "Sun, 01 Jun 2009 00:99:00 GMT",  # range minute
        "Sun, 01 Jun 2009 00:00:99 GMT",  # range second
        "Sun, 31 Dec 9999 23:59:59 -9999",  # range year high
        "Sun, 01 Jan 0000 00:00:00 +9999",  # range year low
        "yesterday",  # too few parts
        "Sun, 16 Dec 2012 1:2:3:4 GMT",  # too many time parts
        "Sun, 16 zzz 2012 11:47:32 GMT",  # bad month name
        "Sun, Dec xx 2012 11:47:32 GMT",  # swapped bad day
        "Sun, zzz 16 2012 11:47:32 GMT",  # swapped bad month
        "Sun, 16 Dec zz 11:47:32 GMT",  # bad year
        # Corrupt timezones
        "Sun, 31 Dec 9999 23:59:59 -999999999999999999999",  # timezone range
        "Sun, 16 Dec 2012 11:47:32 +$$:00",  # bad timezone hour with colon
        "Sun, 16 Dec 2012 11:47:32 -00:$$",  # bad timezone minute with colon
        "Sun, 16 Dec 2012 11:47:32 :",  # bad timezone minute with only a colon
        "Sun, 16 Dec 2012 11:47:32 -00:00:00",  # bad timezone with extra colons
        "Sun, 16 Dec 2012 11:47:32 +$$00",  # bad timezone hour without colon
        "Sun, 16 Dec 2012 11:47:32 +00$$",  # bad timezone minute without colon
        "Sun, 16 Dec 2012 11:47:32 $",  # bad negative timezone minute
    ],
)
def test_invalid_dates(date):
    assert listparser.dates.parse_rfc822(date) is None
