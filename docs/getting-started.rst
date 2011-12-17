Getting started
===============

Because listparser is just a single file, you can copy it to a convenient directory and start the Python interpreter. listparser has a single public function, :py:func:`~listparser.parse`. ::

    >>> import listparser
    >>> result = listparser.parse('http://github.com/kurtmckee/listparser/raw/master/project.opml')

:py:func:`~listparser.parse` can be given a URL, an open file handle, or even an in-memory string.

The dictionary that :py:func:`~listparser.parse` returns will contain several important keys.


The ``meta`` key
----------------

The ``meta`` key contains a dictionary of information about the subscription list, including its title, when it was created and last modified, and who maintains the subscription list::

    >>> result.meta.title
    u'listparser project feeds'
    >>> result.meta.author.keys()
    ['url', 'name', 'email']


The ``feeds`` key
-----------------

The ``feeds`` key is a list of dictionaries. The title and the URL are stored in keys of the same names::

    >>> for i in result.feeds:
    ...     print "%s <%s>" % (i.title, i.url)
    ... 
    listparser blog <http://kurtmckee.livejournal.com/data/atom?tag=listparser>
    listparser releases <http://freecode.com/projects/listparser/announcements.atom>
    listparser changelog <http://github.com/feeds/kurtmckee/commits/listparser/master>


The ``lists`` key
-----------------

OPML subscription lists can point to other subscription lists as easily as they can point to feeds. These subscription lists are placed in the ``lists`` key, and have the same title and URL information as feeds do.


The ``opportunities`` key
-------------------------

Several subscription list formats can contain not just a feed URL but the feed's homepage URL as well. Some software butchers the OPML or RDF+FOAF file creation and outputs only the feed's homepage URL.

When listparser encounters a homepage URL without a corresponding feed URL, it puts that information into the ``opportunities`` key. Opportunities contain the same title and URL information as feeds do, but remember that the URLs are expected to point to a homepage. It is therefore expected that feed readers using listparser will have to run feed and subscription list autodiscovery software against the list of opportunity URLs.

..  seealso:: :doc:`reference/meta`, :doc:`reference/feeds`, :doc:`reference/lists`, :doc:`reference/opportunities`
