What is listparser?
===================

listparser is a Python module that parses subscription lists (also called
reading lists) and returns all of the feeds and subscription lists that it
finds. It supports OPML, RDF+FOAF, and the iGoogle exported settings format,
and runs in Python 2.4 through Python 3.3.

listparser is licensed under the terms of the GNU Lesser General Public License
version 3 or higher.


Usage
=====

>>> import listparser
>>> result = listparser.parse('project.opml')

A dictionary will be returned with several keys:

* ``meta``: a dictionary of information about the subscription list
* ``feeds``: a list of feeds
* ``lists``: a list of subscription lists
* ``version``: a file format identifier
* ``bozo``: 1 if there is a problem with the list, 0 otherwise
* ``bozo_exception``: (if ``bozo`` is 1) a description of the problem

Continuing the example:

>>> result.meta.title
u'listparser project feeds'
>>> len(result.feeds)
2
>>> result.feeds[0].url
u'http://kurtmckee.livejournal.com/data/atom?tag=listparser'

More extensive documentation is available in the docs/ directory,
or online at <https://pythonhosted.org/listparser/>.


Bugs
====

There are going to be bugs. The best way to handle them will be to
isolate the simplest possible document that susses out the bug, add
that document as a test case, and then find and fix the problem.

...you can also just report the bug and leave it to someone else
to fix the problem, but that won't be as much fun for you!

Bugs can be reported at <http://github.com/kurtmckee/listparser/issues>.
