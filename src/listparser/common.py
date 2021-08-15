# This file is part of listparser.
# Copyright 2009-2021 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT
#

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

    def __setattr__(self, name, value):
        self[name] = value
        return value


class CommonMixin:
    def _expect_characters(self, attrs):
        # Most _start_opml_* functions only need to set these two variables,
        # so this function exists to reduce significant code duplication
        self.expect = True
        self._characters = str()
