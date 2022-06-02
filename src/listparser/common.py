# This file is part of listparser.
# Copyright 2009-2022 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

from typing import Callable, Dict, List, Tuple, Union

from .exceptions import ListparserError


namespaces = {
    'http://opml.org/spec2': 'opml',
    'http://www.google.com/ig': 'iGoogle',
    'http://schemas.google.com/GadgetTabML/2008': 'gtml',
    'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf',
    'http://www.w3.org/2000/01/rdf-schema#': 'rdfs',
    'http://xmlns.com/foaf/0.1/': 'foaf',
    'http://purl.org/dc/elements/1.1/': 'dc',
    'http://purl.org/rss/1.0/': 'rss',
    'http://blogs.yandex.ru/schema/foaf/': 'ya',
}


class SuperDict(dict):
    """
    SuperDict is a dictionary object with keys posing as instance attributes.

    ..  code-block:: pycon

        >>> i = SuperDict()
        >>> i.one = 1
        >>> i
        {'one': 1}

    """

    def __getattribute__(self, name):
        if name in self:
            return self[name]
        else:
            return dict.__getattribute__(self, name)


class CommonMixin:
    def __init__(self):
        super().__init__()
        self.harvest = {}
        self.flag_expect_text: bool = False
        self.text: List[str] = []
        self.hierarchy = []
        self.flag_agent = False
        self.flag_feed = False
        self.flag_new_title = False
        self.flag_opportunity = False
        self.flag_group = False

        # found_urls = {url: (append_to_key, obj)}
        self.found_urls: Dict[str, Tuple[str, Dict]] = {}

        # group_objs = [(append_to_key, obj)]
        self.group_objs: List[Tuple[str, Dict]] = []
        self.agent_feeds = []
        self.agent_lists = []
        self.agent_opps = []
        self.foaf_name = []

        # Cache element-to-method name lookups.
        #
        # The dictionary key types vary between parsers:
        #
        # If lxml is the parser, the keys will be strings.
        # If xml.sax is the parser, the keys will be tuples of strings.
        #
        self.start_methods: Dict[Union[Tuple[str, str], str], Callable] = {}
        self.end_methods: Dict[Union[Tuple[str, str], str], Callable] = {}

    def raise_bozo(self, error: Union[Exception, str]):
        self.harvest['bozo'] = True
        if isinstance(error, str):
            self.harvest['bozo_exception'] = ListparserError(error)
        else:
            self.harvest['bozo_exception'] = error

    def expect_text(self, _):
        """Flag that text content is anticipated.

        Many start_* methods only need to prepare for text content.
        This method exists so those start_* methods can be declared
        as aliases for this method.
        """

        self.flag_expect_text = True
        self.text = []

    def get_text(self) -> str:
        """Get text content."""

        text = ''.join(self.text).strip()
        self.text = []
        return text
