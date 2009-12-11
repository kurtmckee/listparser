lists[i].categories
===================

A list of all of the categories associated with the subscription list.

Categories are hierarchical, and are represented as lists of strings. listparser uses the hierarchical groupings in the subscription list in order to assign categories.

..  seealso:: `lists[i].tags <list-tags.html>`_, `feeds[i].categories <feed-categories.html>`_

..  rubric:: Comes from

*   ``/opml/body//outline[type=subscription]/@category`` [#slashes]_
*   ``/opml/body//outline[type=subscription]/ancestor::outline/@text``
*   ``/opml/body//outline[type=subscription]/ancestor::outline/@title``

..  rubric:: Footnotes

.. [#slashes] The ``category`` attribute is a comma-separated string.
