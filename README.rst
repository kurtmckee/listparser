listparser
==========

*Parse OPML subscription lists in Python.*

-------------------------------------------------------------------------------

If you're building a feed reader and you need to parse OPML subscription lists,
you've come to the right place!

listparser makes it easy to parse and use subscription lists in multiple formats.
It supports OPML, RDF+FOAF, and the iGoogle exported settings format,
and runs on Python 3.6+ and on PyPy 3.7.



Usage
=====

..  code-block:: pycon

    >>> import listparser
    >>> result = listparser.parse(open('feeds.opml').read())

A dictionary will be returned with several keys:

*   ``meta``: a dictionary of information about the subscription list
*   ``feeds``: a list of feeds
*   ``lists``: a list of subscription lists
*   ``version``: a format identifier like "opml2"
*   ``bozo``: True if there is a problem with the list, False otherwise
*   ``bozo_exception``: (if ``bozo`` is 1) a description of the problem

For convenience, the result dictionary supports attribute access for its keys.

Continuing the example:

..  code-block:: pycon

    >>> result.meta.title
    'listparser project feeds'
    >>> len(result.feeds)
    2
    >>> result.feeds[0].title, result.feeds[0].url
    ('listparser blog', 'https://kurtmckee.org/tag/listparser')

More extensive documentation is available in the ``docs/`` directory
and online at <https://listparser.readthedocs.io/en/stable/>.


Bugs
====

There are going to be bugs. The best way to handle them will be to
isolate the simplest possible document that susses out the bug, add
that document as a test case, and then find and fix the problem.

...you can also just report the bug and leave it to someone else
to fix the problem, but that won't be as much fun for you!

Bugs can be reported at <https://github.com/kurtmckee/listparser/issues>.
