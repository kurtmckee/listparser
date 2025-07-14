..
    This file is part of listparser.
    Copyright 2009-2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT

objects[i].tags
===============

A list of all of the tags associated with the feed, subscription list,
or opportunity object. They are copied from the ``categories`` key if
the category is one level deep. As an example:

..  code-block:: xml

    <outline text="sports">
        <outline type="rss" text="ESPN" xmlUrl="http://espn.com/feed" />
    </outline>

In this example, there is one tag: ``sports``.

..  seealso:: :doc:`object-categories`

..  rubric:: Comes from

*   ``/opml/body//outline/@category`` [#noslashes]_
*   ``/opml/body/outline/outline/parent::outline/@text``
*   ``/opml/body/outline/outline/parent::outline/@title``
*   ``/rdf:RDF/foaf:Group/foaf:name``
*   ``/rdf:RDF//foaf:Agent/foaf:name``

..  rubric:: Footnotes

.. [#noslashes] The ``category`` attribute is a comma-separated string.
