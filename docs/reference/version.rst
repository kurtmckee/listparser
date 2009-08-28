version
=======

``version`` is a string that represents what version of OPML the subscription list claims to be following. It always exists, although it may be an empty string if the document is not an OPML file (or is severely malformed).

These are the known values:

opml1
    `OPML 1.0 and 1.1 <http://www.opml.org/spec>`_ [#opml11]_

opml2
    `OPML version 2.0 <http://www.opml.org/spec2>`_

opml
    An OPML file with an unknown or unspecified version


..  rubric:: Footnotes

..  [#opml11] `OPML 1.1 files are treated as OPML 1.0 files. <http://www.opml.org/stories/storyReader$11>`_
