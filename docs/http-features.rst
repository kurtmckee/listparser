..
    This file is part of listparser.
    Copyright 2009-2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT

HTTP Features
=============

If the requests package is installed, listparser will be able to accept HTTP and HTTPS URL's for parsing.
For example:

..  code-block:: pycon

    >>> result = listparser.parse("https://domain.example/feeds.opml")

A 30-second timeout is set on all requests.

If requests is not installed, listparser will return a dictionary with the following data:

..  code-block:: pycon

    >>> listparser.parse("https://domain.example/feeds.opml")
    {
        'bozo': 1,
        'bozo_exception': ListparserError('requests is not installed...')
    }
