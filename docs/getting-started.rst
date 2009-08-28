Getting started
===============

Because listparser is just a single file, you can simply copy it into a convenient directory and start the Python interpreter. listparser has a single public function, ``parse()``. ::

    >>> import listparser
    >>> result = listparser.parse('http://github.com/kurtmckee/listparser/raw/master/project.opml')

``parse()`` can be given a URL, a open file handle, or even an in-memory string.

The dictionary that ``parse()`` returns will contain several important keys.


The ``meta`` key
----------------

The ``meta`` key contains a dictionary of information about the subscription list, including its title, when it was created and last modified, and who maintains the list::

    >>> result.meta.title
    u'listparser project feeds'
    >>> result.meta.author.keys()
    ['url', 'name', 'email']


The ``feeds`` key
-----------------

The ``feeds`` key is a Python list of dictionaries. The title and the URL are stored in keys of the same names::

    >>> for i in result.feeds:
    ...     print "%s <%s>" % (i.title, i.url)
    ... 
    listparser blog <http://kurtmckee.livejournal.com/data/atom?tag=listparser>
    listparser releases <http://freshmeat.net/projects/listparser/releases.atom>
    listparser changelog <http://github.com/feeds/kurtmckee/commits/listparser/master>


The ``lists`` key
-----------------

OPML subscription lists can point to other subscription lists as easily as they can point to feeds. These subscriptions are placed in the ``lists`` key, and have the same title and URL information as feeds do.


..  seealso:: `meta <reference/meta.html>`_, `feeds <reference/feeds.html>`_, `lists <reference/lists.html>`_
