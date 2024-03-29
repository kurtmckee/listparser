listparser
==========

*Parse OPML subscription lists in Python.*

-------------------------------------------------------------------------------

If you're building a feed reader and you need to parse OPML subscription lists,
you've come to the right place!

listparser makes it easy to parse and use subscription lists in multiple formats.
It supports OPML, RDF+FOAF, and the iGoogle exported settings format,
and runs on Python 3.8+ and on PyPy 3.8.



Usage
=====

..  code-block:: pycon

    >>> import listparser
    >>> result = listparser.parse(open("feeds.opml").read())

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
`and online <https://listparser.readthedocs.io/en/latest/>`_.


Bugs
====

There are going to be bugs. The best way to handle them will be to
isolate the simplest possible document that susses out the bug, add
that document as a test case, and then find and fix the problem.

...you can also just report the bug and leave it to someone else
to fix the problem, but that won't be as much fun for you!

`Bugs can be reported on GitHub <https://github.com/kurtmckee/listparser/issues>`_.


Git workflow
============

listparser basically follows the git-flow methodology:

*   Features and changes are developed in branches off the ``main`` branch.
    They merge back into the ``main`` branch.
*   Feature releases branch off the ``main`` branch.
    The project metadata is updated (like the version and copyright years),
    and then the release branch merges into the ``releases`` branch.
    The ``releases`` branch is then tagged, and then it is merged back into ``main``.
*   Hotfixes branch off the ``releases`` branch.
    As with feature releases, the project metadata is updated,
    the hotfix branch merges back into the ``releases`` branch,
    which is then tagged and merged back into ``main``.


Development
===========

To set up a development environment, follow these steps at a command line:

..  code-block:: shell

    # Set up a virtual environment.
    python -m venv .venv

    # Activate the virtual environment in Linux:
    . .venv/bin/activate

    # ...or in Windows Powershell:
    & .venv/Scripts/Activate.ps1

    # Install dependencies.
    python -m pip install -U pip setuptools wheel
    python -m pip install poetry pre-commit tox scriv
    poetry install --all-extras

    # Enable pre-commit.
    pre-commit install

    # Run the unit tests.
    tox


When submitting a PR, be sure to create and edit a changelog fragment.

..  code-block:: shell

    scriv create


The changelog fragment will be created in the ``changelog.d/`` directory.
Edit the file to describe the changes you've made.
