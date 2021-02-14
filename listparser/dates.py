# This file is part of listparser.
# Copyright 2009-2021 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import datetime
from typing import Dict, Optional, Set, Tuple


day_names: Set[str] = {
    'mon',
    'tue',
    'wed',
    'thu',
    'fri',
    'sat',
    'sun',
}

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

timezone_names: Dict[str, int] = {
    'ut': 0,
    'gmt': 0,
    'z': 0,
    'adt': -3,
    'ast': -4,
    'at': -4,
    'edt': -4,
    'est': -5,
    'et': -5,
    'cdt': -5,
    'cst': -6,
    'ct': -6,
    'mdt': -6,
    'mst': -7,
    'mt': -7,
    'pdt': -7,
    'pst': -8,
    'pt': -8,
    'a': -1,
    'n': 1,
    'm': -12,
    'y': 12,
}


def rfc822(date: str) -> Optional[datetime.datetime]:
    """Parse RFC 822 dates and times.

    http://tools.ietf.org/html/rfc822#section-5

    There are some formatting differences that are accounted for:
    1. Years may be two or four digits.
    2. The month and day can be swapped.
    3. Additional timezone names are supported.
    4. A default time and timezone are assumed if only a date is present.
    """

    parts = date.lower().split()
    if len(parts) < 5:
        # Assume that the time and timezone are missing
        parts.extend(('00:00:00', '0000'))
    # Remove the day name
    if parts[0][:3] in day_names:
        parts = parts[1:]
    if len(parts) < 5:
        # If there are still fewer than five parts, there's not enough
        # information to interpret this
        return None
    try:
        day = int(parts[0])
    except ValueError:
        # Check if the day and month are swapped
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
    if not month:
        return None
    try:
        year = int(parts[2])
    except ValueError:
        return None
    # Normalize two-digit years:
    # Anything in the 90's is interpreted as 1990 and on
    # Anything 89 or less is interpreted as 2089 or before
    if len(parts[2]) <= 2:
        year += (1900, 2000)[year < 90]
    time_parts = parts[3].split(':')
    time_parts = time_parts + (['0'] * (3 - len(time_parts)))
    try:
        (hour, minute, second) = map(int, time_parts)
    except ValueError:
        return None
    tz_min = 0
    # Strip 'Etc/' from the timezone
    if parts[4].startswith('etc/'):
        parts[4] = parts[4][4:]
    # Normalize timezones that start with 'gmt':
    # GMT-05:00 => -0500
    # GMT => GMT
    if parts[4].startswith('gmt'):
        parts[4] = ''.join(parts[4][3:].split(':')) or 'gmt'
    # Handle timezones like '-0500', '+0500', and 'EST'
    if parts[4] and parts[4][0] in ('-', '+'):
        try:
            tz_hour = int(parts[4][1:3])
            tz_min = int(parts[4][3:])
        except ValueError:
            return None
        if parts[4].startswith('-'):
            tz_hour = tz_hour * -1
            tz_min = tz_min * -1
    else:
        tz_hour = timezone_names.get(parts[4], 0)
    # Create the datetime object and timezone delta objects
    try:
        stamp = datetime.datetime(year, month, day, hour, minute, second)
    except ValueError:
        return None
    delta = datetime.timedelta(0, 0, 0, 0, tz_min, tz_hour)
    # Return the date and timestamp in a UTC 9-tuple
    try:
        return stamp - delta
    except OverflowError:
        return None


rfc822_month_names: Tuple[str, ...] = (
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
)

rfc822_day_names: Tuple[str, ...] = (
    'Mon',
    'Tue',
    'Wed',
    'Thu',
    'Fri',
    'Sat',
    'Sun',
)

rfc822_pattern = '{day}, {d:02} {month} {y:04} {h:02}:{m:02}:{s:02} GMT'


def to_rfc822(date: datetime.datetime) -> str:
    """Convert a datetime object to an RFC822-formatted string.

    The datetime `strftime` method is subject to locale-specific
    day and month names, so this function hardcodes the conversion.
    """

    return rfc822_pattern.format(
        day=rfc822_day_names[date.weekday()],
        d=date.day,
        month=rfc822_month_names[date.month - 1],
        y=date.year,
        h=date.hour,
        m=date.minute,
        s=date.second,
    )
