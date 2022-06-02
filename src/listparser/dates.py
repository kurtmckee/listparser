# This file is part of listparser.
# Copyright 2009-2022 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import datetime
from typing import Dict, Optional


months: Dict[str, int] = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12,
}

timezones: Dict[str, int] = {
    # Universal Time
    'ut': 0,
    'utc': 0,
    'gmt': 0,

    # North America
    'est': -5,
    'edt': -4,
    'cst': -6,
    'cdt': -5,
    'mst': -7,
    'mdt': -6,
    'pst': -8,
    'pdt': -7,

    # Military
    'z': 0,
    'a': -1,
    'n': +1,
    'm': -12,
    'y': +12,
}


def parse_rfc822(date: str) -> Optional[datetime.datetime]:
    """Parse RFC 822 dates and times.

    https://tools.ietf.org/html/rfc822#section-5

    The basic format is:

    ..  code-block:: text

        [ day "," ] dd mmm [yy]yy hh:mm[:ss] zzz

    Note that RFC 822 only specifies an explicit comma,
    but fails to make whitespace mandatory.

    Some non-standard formatting differences are allowed:

    *   Whitespace is assumed to separate each part of the timestamp.
    *   Years may be two or four digits.
        This is explicitly allowed in the OPML specification.
    *   The month name and day can be swapped.
    *   Timezones may be prefixed with "Etc/".
    *   If the time and/or timezone are missing,
        midnight and GMT will be assumed.
    *   "UTC" is supported as a timezone name.

    """

    parts = date.rpartition(',')[2].lower().split()
    if len(parts) == 3:
        # Assume that the time is missing.
        parts.append('00:00:00')
    if len(parts) == 4:
        # Assume that the timezone is missing.
        parts.append('gmt')
    elif len(parts) != 5:
        # If there are not exactly five parts then this isn't an
        # RFC 822 date and time.
        return None

    # Parse the day and month.
    try:
        day = int(parts[0])
    except ValueError:
        # Check if the day and month are swapped.
        if months.get(parts[0][:3]):
            try:
                day = int(parts[1])
            except ValueError:
                return None
            else:
                parts[1] = parts[0]
        else:
            return None
    month = months.get(parts[1][:3])
    if month is None:
        return None

    # Parse the year.
    try:
        year = int(parts[2])
    except ValueError:
        return None
    # Normalize two-digit years:
    #
    # * Anything in the 90's is interpreted as the 1990's.
    # * Anything 89 or before is interpreted as 2089 or before.
    #
    if year < 100:
        if year >= 90:
            year += 1900
        else:
            year += 2000

    # Parse the time.
    time_parts = parts[3].split(':')
    time_parts += ['0'] * (3 - len(time_parts))
    try:
        hour, minute, second = map(int, time_parts)
    except ValueError:
        return None

    # Parse named timezones.
    tz_min = 0
    # Strip 'Etc/' from the timezone name.
    timezone = parts[4]
    if timezone.startswith('etc/'):
        timezone = timezone[4:] or 'gmt'
    # Normalize timezones that start with 'gmt':
    #
    # * gmt-05:00 => -05:00
    # * gmt => gmt
    #
    if timezone.startswith('gmt'):
        timezone = timezone[3:] or 'gmt'
    tz_hour = timezones.get(timezone)

    # Parse numeric timezones like '-0500' and '+0500'.
    if tz_hour is None:
        try:
            tz_left, tz_right = timezone.split(':')
            tz_hour = int(tz_left)
            tz_min = int(tz_right)
        except ValueError:
            # Perhaps there was no ':' in *timezone*.
            try:
                tz_hour = int(timezone[:-2])
                tz_min = int(timezone[-2:])
            except ValueError:
                return None
        if tz_hour < 0:
            tz_min = tz_min * -1

    # Create the datetime and timezone offset return values.
    try:
        return datetime.datetime(
            year, month, day,
            hour, minute, second,
            tzinfo=datetime.timezone(
                datetime.timedelta(minutes=(tz_hour * 60) + tz_min)
            ),
        )
    except (ValueError, OverflowError):
        return None
