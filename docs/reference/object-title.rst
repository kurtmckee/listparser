objects[i].title
================

The title of the feed, subscription list, or opportunity object. It is not normalized except for the stripping of whitespace.

..  note::

    The ``opml:outline`` element's ``text`` and ``title`` attributes differ in function. Many feed readers keep track of the feed's original title while allowing users to change the title that they see. When their subscription list is exported, the ``opml:outline`` element's ``text`` attribute should contain the user's preferred title, and the ``title`` attribute should contain the original title.

    In practice, however, some softwares don't use the ``text`` attribute at all. Therefore, ``feeds[i].title`` is filled from the ``text`` attribute or, if that isn't available, the ``title`` attribute. For example:

    ..  highlight:: xml

    ::

        <outline text="Hal Tucker" title="Confessions of a Cliffhanger (Latest 10 entries)"
            type="rss" xmlUrl="http://capt-hottub.xanga.com/rss" />

    And here is the title returned by listparser:

    ..  highlight:: python

    ::

        >>> result.feeds[0].title
        u'Hal Tucker'

..  rubric:: Comes from

*   ``/opml/body//outline/@text``
*   ``/opml/body//outline/@title``
*   ``/rdf:RDF//foaf:Agent/foaf:name``
*   ``/rdf:RDF//foaf:Agent/foaf:member_name``
