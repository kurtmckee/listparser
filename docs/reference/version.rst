version
=======

``version`` is a string that represents the format of the subscription
list. It always exists, although it may be an empty string if the
subscription list format is not recognized.

These are the possible values:

opml1
    `OPML 1.0 and 1.1 <http://dev.opml.org/spec1.html>`_ [#opml11]_

opml2
    `OPML version 2.0 <http://dev.opml.org/spec2.html>`_

opml
    An OPML file with an unknown or unspecified version

rdf
    `RDF+FOAF <http://xmlns.com/foaf/spec/>`_

igoogle
    iGoogle exported settings format [#igoog_export]_


..  rubric:: Footnotes

..  [#opml11] `OPML 1.1 files are treated as OPML 1.0 files. <http://dev.opml.org/spec2.html#whatIsAnLtopmlgt>`_
..  [#igoog_export] `How to export your iGoogle page settings <https://googlesystem.blogspot.com/2008/04/backup-your-igoogle-page.html>`_
