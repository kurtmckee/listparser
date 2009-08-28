lists[i].tags
=============

A list of all of the tags associated with the subscription list.

Although tags can be specified in the ``category`` attribute of an ``outline`` element, listparser will also copy over any categories that are only one level deep, and will additionally copy in the text of a parent ``outline`` element if the hierarchy is only one level deep. As an example:

..  highlight:: xml

::

    <outline text="sports">
        <outline text="ESPN" type="include" url="http://espn.com/~user/subscriptions"
            category="baseball,/golf"
        />
    </outline>

In this example, there are three tags: "sports", "baseball", and "golf".

..  seealso:: `lists[i].categories <list-categories.html>`_

..  rubric:: Comes from

*   ``/opml/body//outline[type=subscription]/@category`` [#noslashes]_
*   ``/opml/body/outline/outline[type=subscription]/parent::outline/@text``
*   ``/opml/body/outline/outline[type=subscription]/parent::outline/@title``

..  rubric:: Footnotes

.. [#noslashes] The ``category`` attribute is a comma-separated string; any values not containing slashes are considered to be tags.
