# This file is part of listparser.
# Copyright 2009-2022 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

import io
from typing import Any, Dict, Optional, Tuple, Union

try:
    import requests
    import urllib3.exceptions
except ImportError:
    requests = None  # type: ignore
    urllib3 = None  # type: ignore

try:
    # lxml lacks mypy stubs at the time of writing.
    import lxml.etree  # type: ignore
except ImportError:
    lxml = None  # type: ignore

from . import common, parsers
from .exceptions import ListparserError

__author__ = "Kurt McKee <contactme@kurtmckee.org>"
__url__ = "https://github.com/kurtmckee/listparser"
__version__ = "0.19"


def parse(parse_obj: Union[str, bytes]) -> common.SuperDict:
    """Parse a subscription list and return a dict containing the results.

    *parse_obj* must be one of the following:

    *   a string containing a URL
    *   a string or bytes object containing an XML document

    The dictionary returned will contain all of the parsed information,
    HTTP response headers (if applicable), and any exception encountered.
    """

    guarantees: Dict[str, Any] = {
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

    handler: Union[parsers.LxmlHandler, parsers.HTMLHandler]
    if lxml is not None:
        handler = parsers.LxmlHandler()
        handler.harvest.update(guarantees)
        content_file = io.BytesIO(content)
        parser = lxml.etree.HTMLParser(target=handler, recover=True)
        lxml.etree.parse(content_file, parser)
    else:
        handler = parsers.HTMLHandler()
        handler.harvest.update(guarantees)
        handler.feed(content.decode())

    harvest = common.SuperDict(handler.harvest)
    handler.close()
    del handler

    return harvest


def get_content(obj) -> Tuple[Optional[bytes], Dict]:
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