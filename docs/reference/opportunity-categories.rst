opportunities[i].categories
===========================

A list of all of the categories associated with the opportunity URL. Categories are hierarchical, and are represented as lists of strings.

For a full explanation of categories in listparser, see `feeds[i].categories <feed-categories.html>`_.

..  seealso:: `opportunities[i].tags <opportunity-tags.html>`_

..  rubric:: Comes from

*   ``/opml/body//outline/@category`` [#slashes]_
*   ``/opml/body//outline/ancestor::outline/@text``
*   ``/opml/body//outline/ancestor::outline/@title``
*   ``/rdf:RDF//foaf:Agent/foaf:name``

..  rubric:: Footnotes

.. [#slashes] The ``category`` attribute is a comma-separated string.
