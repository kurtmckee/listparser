feeds[i].title
==============

The title of the feed. It is not normalized except for the stripping of whitespace.

..  note::

    ``feeds[i].title`` and ``feeds[i].claims.title`` differ in function. Many feed readers keep track of the feed's original title while allowing users to change the feed title that they see. When this subscription list is exported, the ``outline`` element's ``text`` attribute should contain the user's preferred title, and the ``title`` attribute should contain the original title.

    In practice, however, some software deviates from the specification. Therefore, ``feeds[i].title`` is filled from the ``text`` or the ``title`` attribute (in that order). ``feeds[i].claims.title`` is filled from the ``title`` attribute if it exists. For example:

    ..  highlight:: xml

    ::

        <outline text="Hal Tucker" title="Confessions of a Cliffhanger (Latest 10 entries)"
            type="rss" xmlUrl="http://capt-hottub.xanga.com/rss" />

    And here are the values returned by listparser:

    ..  highlight:: python

    ::

        >>> result.feeds[0].title
        u'Hal Tucker'
        >>> result.feeds[0].claims.title
        u'Confessions of a Cliffhanger (Latest 10 entries)'

..  rubric:: Comes from

*   ``/opml/body//outline[type=feed]/@text``
*   ``/opml/body//outline[type=feed]/@title``
