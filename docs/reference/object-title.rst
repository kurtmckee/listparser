objects[i].title
================

The title of the feed, subscription list, or opportunity object. It is
not normalized except for the stripping of whitespace.

..  note::

    The ``opml:outline`` element's ``text`` and ``title`` attributes
    differ in function. Many feed readers keep track of the feed's
    original title while allowing users to change the title that they
    see. When their subscription list is exported, the ``opml:outline``
    element's ``text`` attribute should contain the user's preferred
    title, and the ``title`` attribute should contain the original title.

    In practice, however, some software doesn't use the ``text``
    attribute at all. Therefore, ``feeds[i].title`` is filled from the
    ``text`` attribute or, if that isn't available, the ``title``
    attribute. For example:

    ..  code-block:: xml

        <outline text="*text* attribute" title="*title* attribute"
            type="rss" xmlUrl="https://domain.example/feed" />

    And here is the title returned by listparser:

    ..  code-block:: pycon

        >>> result.feeds[0].title
        '*text* attribute'

..  rubric:: Comes from

*   ``/opml/body//outline/@text``
*   ``/opml/body//outline/@title``
*   ``/rdf:RDF//foaf:Agent/foaf:name``
*   ``/rdf:RDF//foaf:Agent/foaf:member_name``
