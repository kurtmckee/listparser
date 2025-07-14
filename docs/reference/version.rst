..
    This file is part of listparser.
    Copyright 2009-2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT

version
=======

``version`` is a string that represents the format of the subscription
list. It always exists, although it may be an empty string if the
subscription list format is not recognized.

These are the possible values:

opml1
    :doc:`OPML 1.0 and 1.1 </specifications/opml-1.0>` [#opml11]_

opml2
    :doc:`OPML version 2.0 </specifications/opml-2.0>`

opml
    An OPML file with an unknown or unspecified version

rdf
    `RDF+FOAF <http://xmlns.com/foaf/spec/>`_


..  rubric:: Footnotes

..  [#opml11]

    `OPML 1.1 files are treated as OPML 1.0 files. <https://web.archive.org/web/20070221092352/http://www.opml.org:80/stories/storyReader$11>`_

    In 2001, Dave Winer announced that OPML 1.1 would include a ``<cloud>`` tag.
    In 2005, the original announcement was modified to state that the project was dropped,
    and included this message:

        [If] you see an OPML 1.1 file, you should treat it like an OPML 1.0 file. That's it. Enjoy!
