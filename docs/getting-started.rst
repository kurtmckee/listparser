Getting started
===============

Use pip to install listparser.

To support retrieving and parsing of URL's, add ``[http]`` to the command
so the requests package will be installed as well.

To parse broken XML, add ``[lxml]`` to the command
so the lxml package will be installed as well.

..  code-block:: shell

    python -m pip install listparser[http,lxml]

You don't have to install lxml or requests but it will reduce listparser's functionality.


listparser has a single public function, :py:func:`~listparser.parse`.

..  code-block:: pycon

    >>> import listparser
    >>> result = listparser.parse("https://raw.githubusercontent.com/kurtmckee/listparser/main/feeds.opml")

:py:func:`~listparser.parse` can be given a URL, an open file handle,
or even an in-memory string.

The dictionary that :py:func:`~listparser.parse` returns will contain
several important keys.


The ``meta`` key
----------------

The ``meta`` key contains a dictionary of information about the
subscription list, including its title, when it was created and last
modified, and who maintains the subscription list.

..  code-block:: pycon

    >>> result.meta.title
    'listparser project feeds'
    >>> result.meta.author.keys()
    dict_keys(['name', 'email', 'url'])


The ``feeds`` key
-----------------

The ``feeds`` key is a list of dictionaries.
The title and the URL are stored in keys of the same names.

..  code-block:: pycon

    >>> for feed in result.feeds:
    ...     print(f"{feed.title} <{feed.url}>")
    ...
    listparser blog <https://kurtmckee.org/tag/listparser/feed>
    listparser changelog <https://github.com/kurtmckee/listparser/commits/main.atom>



The ``lists`` key
-----------------

OPML subscription lists can point to other subscription lists as easily
as they can point to feeds. These subscription lists are placed in the
``lists`` key, and have the same title and URL information that feeds do.


The ``opportunities`` key
-------------------------

Several subscription list formats can contain not just a feed URL but
the feed's homepage URL as well. Some software butchers the OPML or
RDF+FOAF file creation and outputs only the feed's homepage URL.

When listparser encounters a homepage URL without a corresponding feed
URL, it puts that information into the ``opportunities`` key.
Opportunities contain the same title and URL information as feeds do,
but remember that the URLs are expected to point to a homepage. It is
therefore expected that feed readers using listparser will have to run
feed and subscription list autodiscovery software against the list of
opportunity URLs.


..  seealso::

    :doc:`reference/meta`,
    :doc:`reference/feeds`,
    :doc:`reference/lists`,
    :doc:`reference/opportunities`
