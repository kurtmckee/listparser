# This file is part of listparser.
# Copyright 2009-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import datetime
import unittest

import listparser
from listparser import dates


class TestIso8601Dates(unittest.TestCase):
    """Test handling of ISO 8601 dates in OPML files."""

    def test_iso8601_date_parsing(self):
        """Test that ISO 8601 dates are correctly parsed by the new parser."""
        # Test various ISO 8601 formats
        test_cases = [
            # Basic format
            (
                "2025-04-07T19:52:30Z",
                datetime.datetime(2025, 4, 7, 19, 52, 30, tzinfo=datetime.timezone.utc),
            ),
            # With milliseconds
            (
                "2025-04-07T19:52:30.941Z",
                datetime.datetime(
                    2025, 4, 7, 19, 52, 30, 941000, tzinfo=datetime.timezone.utc
                ),
            ),
            # With microseconds (truncated)
            (
                "2025-04-07T19:52:30.941378073Z",
                datetime.datetime(
                    2025, 4, 7, 19, 52, 30, 941378, tzinfo=datetime.timezone.utc
                ),
            ),
            # With timezone offset
            (
                "2025-04-07T19:52:30+02:00",
                datetime.datetime(
                    2025,
                    4,
                    7,
                    19,
                    52,
                    30,
                    tzinfo=datetime.timezone(datetime.timedelta(hours=2)),
                ),
            ),
            # With timezone offset (no colon)
            (
                "2025-04-07T19:52:30-0700",
                datetime.datetime(
                    2025,
                    4,
                    7,
                    19,
                    52,
                    30,
                    tzinfo=datetime.timezone(datetime.timedelta(hours=-7)),
                ),
            ),
            # With space instead of T
            (
                "2025-04-07 19:52:30Z",
                datetime.datetime(2025, 4, 7, 19, 52, 30, tzinfo=datetime.timezone.utc),
            ),
        ]

        for input_date, expected_datetime in test_cases:
            with self.subTest(input_date=input_date):
                result = dates.parse_iso8601(input_date)
                self.assertEqual(result, expected_datetime)

                # Also test with the generic parse_date function
                result = dates.parse_date(input_date)
                self.assertEqual(result, expected_datetime)

    def test_opml_iso8601(self):
        """Test that OPML files with ISO 8601 dates are now processed without errors."""
        # Create simple XML with ISO 8601 date
        data = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
    <head>
        <title>ISO 8601 Date Test</title>
        <dateCreated>2025-04-07T19:52:30.941378073Z</dateCreated>
    </head>
    <body>
        <outline title="Test Feed"
            xmlUrl="https://example.com/feed"
            text="Test Feed"
            type="rss">
        </outline>
    </body>
</opml>"""

        # Parse the XML
        result = listparser.parse(data)

        # Verify that there's no bozo error
        self.assertEqual(result["bozo"], 0)

        # Verify the parsed date
        self.assertIsNotNone(result["meta"]["created_parsed"])
        self.assertEqual(
            result["meta"]["created_parsed"],
            datetime.datetime(
                2025, 4, 7, 19, 52, 30, 941378, tzinfo=datetime.timezone.utc
            ),
        )
