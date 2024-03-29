# This file is part of listparser.
# Copyright 2009-2024 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

from __future__ import annotations

import io
import typing as t

try:
    import requests
    import urllib3.exceptions
except ImportError:
    requests = None  # type: ignore[assignment]
    urllib3 = None  # type: ignore[assignment]

try:
    import lxml.etree
except ImportError:
    lxml = None  # type: ignore[assignment]

from . import common, foaf, igoogle, opml, xml_handler
from .exceptions import ListparserError

__author__ = "Kurt McKee <contactme@kurtmckee.org>"
__url__ = "https://github.com/kurtmckee/listparser"
__version__ = "0.19"


Handler = type(
    "Handler",
    (
        opml.OpmlMixin,
        foaf.FoafMixin,
        igoogle.IgoogleMixin,
        xml_handler.XMLHandler,
    ),
    {},
)


def parse(parse_obj: str | bytes) -> common.SuperDict:
    """Parse a subscription list and return a dict containing the results.

    *parse_obj* must be one of the following:

    *   a string containing a URL
    *   a string or bytes object containing an XML document

    The dictionary returned will contain all of the parsed information,
    HTTP response headers (if applicable), and any exception encountered.
    """

    guarantees: dict[str, t.Any] = {
        "bozo": False,
        "bozo_exception": None,
        "feeds": [],
        "lists": [],
        "opportunities": [],
        "meta": common.SuperDict(),
        "version": "",
    }
    content, info = get_content(parse_obj)
    guarantees.update(info)
    if not content:
        return common.SuperDict(guarantees)

    handler = Handler()
    handler.harvest.update(guarantees)

    if lxml is not None:
        content_file = io.BytesIO(content)
        parser = lxml.etree.HTMLParser(target=handler, recover=True)
        lxml.etree.parse(content_file, parser)
    else:
        handler.feed(content.decode())

    harvest = common.SuperDict(handler.harvest)
    handler.close()
    del handler

    return harvest


def get_content(obj: bytes | str) -> tuple[bytes | None, dict[str, t.Any]]:
    if isinstance(obj, bytes):
        return obj, {"bozo": False, "bozo_exception": None}
    elif not isinstance(obj, str):
        # Only str and bytes objects can be parsed.
        error = ListparserError("parse() called with unparsable object")
        return None, {"bozo": True, "bozo_exception": error}
    elif not obj.startswith(("http://", "https://")):
        # It's not a URL, so it must be treated as an XML document.
        return obj.encode("utf8"), {
            "bozo": False,
            "bozo_exception": None,
        }

    # It's a URL. Confirm requests is installed.
    elif requests is None:
        message = f"requests is not installed so {obj} cannot be retrieved"
        return None, {
            "bozo": True,
            "bozo_exception": ListparserError(message),
        }

    headers = {"user-agent": f"listparser/{__version__} +{__url__}"}
    try:
        response = requests.get(obj, headers=headers, timeout=30)
    except (
        requests.exceptions.RequestException,
        urllib3.exceptions.HTTPError,
    ) as error:
        return None, {"bozo": True, "bozo_exception": error}

    return response.text.encode("utf8"), {
        "bozo": False,
        "bozo_exception": None,
    }
