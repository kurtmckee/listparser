lists[i].tags
=============

A list of all of the tags associated with the subscription. They are copied from the ``categories`` key if the category is one level deep.

..  seealso:: `lists[i].categories <list-categories.html>`_, `feeds[i].categories <feed-categories.html>`_

..  rubric:: Comes from

*   ``/opml/body//outline[type=subscription]/@category`` [#noslashes]_
*   ``/opml/body/outline/outline[type=subscription]/parent::outline/@text``
*   ``/opml/body/outline/outline[type=subscription]/parent::outline/@title``

..  rubric:: Footnotes

.. [#noslashes] The ``category`` attribute is a comma-separated string.
