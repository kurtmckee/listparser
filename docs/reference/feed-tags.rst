feeds[i].tags
=============

A list of all of the tags associated with the feed.

Although tags can be specified in the ``category`` attribute of an ``outline`` element, listparser will also copy over any categories that are only one level deep, and will additionally copy in the text of a parent ``outline`` element if the hierarchy is only one level deep. As an example:

..  highlight:: xml

::

    <outline text="sports">
        <outline category="baseball,/golf" text="ESPN" type="rss" xmlUrl="http://espn.com/feed" />
    </outline>

In this example, there are three tags: "sports", "baseball", and "golf".

..  seealso:: `feeds[i].categories <feed-categories.html>`_

..  rubric:: Comes from

*   ``/opml/body//outline[type=feed]/@category`` [#noslashes]_
*   ``/opml/body/outline/outline[type=feed]/parent::outline/@text``
*   ``/opml/body/outline/outline[type=feed]/parent::outline/@title``
*   ``/gtml:GadgetTabML//gtml:Tab/@title``

..  rubric:: Footnotes

.. [#noslashes] The ``category`` attribute is a comma-separated string; any values not containing slashes are considered to be tags.
