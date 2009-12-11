feeds[i].tags
=============

A list of all of the tags associated with the feed. They are copied from the ``categories`` key if the category is one level deep. As an example:

..  highlight:: xml

::

    <outline text="sports">
        <outline type="rss" text="ESPN" xmlUrl="http://espn.com/feed" />
    </outline>

In this example, there is one tag: ``sports``.

..  seealso:: `feeds[i].categories <feed-categories.html>`_

..  rubric:: Comes from

*   ``/opml/body//outline[type=feed]/@category`` [#noslashes]_
*   ``/opml/body/outline/outline[type=feed]/parent::outline/@text``
*   ``/opml/body/outline/outline[type=feed]/parent::outline/@title``
*   ``/gtml:GadgetTabML//gtml:Tab/@title``
*   ``/rdf:RDF/foaf:Group/foaf:name``

..  rubric:: Footnotes

.. [#noslashes] The ``category`` attribute is a comma-separated string.
