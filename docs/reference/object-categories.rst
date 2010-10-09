objects[i].categories
=====================

A list of all of the categories associated with the feed, subscription list, or opportunity object.

Categories are hierarchical, and are represented as lists of strings. listparser uses the hierarchical groupings in the subscription list in order to assign categories. Here is an example in OPML:

..  highlight:: xml

::

    <outline text="news">
        <outline text="sports">
            <outline type="rss" text="ESPN" xmlUrl="http://espn.com/feed" />
        </outline>
    </outline>

In this example, the category hierarchy is ``["news", "sports"]``. In the OPML format, listparser will also use the ``category`` attribute of the ``opml:outline`` element as a source of categorization information. 

..  seealso:: :doc:`object-tags`

..  rubric:: Comes from

*   ``/opml/body//outline/@category`` [#slashes]_
*   ``/opml/body//outline/ancestor::outline/@text``
*   ``/opml/body//outline/ancestor::outline/@title``
*   ``/gtml:GadgetTabML//gtml:Tab/@title``
*   ``/rdf:RDF/foaf:Group/foaf:name``
*   ``/rdf:RDF//foaf:Agent/foaf:name``

..  rubric:: Footnotes

.. [#slashes] The ``category`` attribute is a comma-separated string.
