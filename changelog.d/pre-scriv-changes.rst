Added
-----

*   Add support for Python 3.6 through Python 3.9.


Removed
-------

*   Drop support for Python 2.4 through Python 3.5.
*   Drop support for Jython for lack of Python 3 compatibility.
*   Drop support for IronPython for lack of ipy XML parsers.


Changed
-------

*   Split the codebase into multiple files.
*   Use tox to automate testing across multiple interpreters and versions.
*   Migrate to pytest for unit testing.
*   Remove dependence on the six module.
*   Add type annotations.
*   Remove compatibility code.
*   Migrate to Poetry and ``pyproject.toml`` for project configuration.
*   Change the license from LGPLv3 to MIT.
*   Use scriv to manage the CHANGELOG.
