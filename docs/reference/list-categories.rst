lists[i].categories
===================

A list of all of the categories associated with the subscription.

Categories are hierarchical, and are represented as lists of strings. Although categories can be specified in the ``category`` attribute of an ``outline`` element, listparser will also use the ``outline`` element hierarchy as a source of categorization information. As an example:

..  highlight:: xml

::

    <outline text="news">
        <outline text="sports">
            <outline text="Golf news" type="include" url="http://espn.com/~user/subscriptions"
                category="/golf/tiger,/golf/palmer" />
        </outline>
    </outline>

In this example, there are three categories:

*   ["news", "sports"]
*   ["tv", "golf"]
*   ["tv", "baseball"]

..  seealso:: `lists[i].tags <list-tags.html>`_

..  rubric:: Comes from

*   ``/opml/body//outline[type=subscription]/@category`` [#slashes]_
*   ``/opml/body//outline[type=subscription]/ancestor::outline/@text``
*   ``/opml/body//outline[type=subscription]/ancestor::outline/@title``

..  rubric:: Footnotes

.. [#slashes] The ``category`` attribute is a comma-separated string; any values containing slashes are considered to be categories.
