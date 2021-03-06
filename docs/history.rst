History
=======


Unreleased changes
------------------

    * Split the codebase into multiple files (drops Python 2.4 support)
    * Use tox to automate testing across multiple interpreters and versions
    * Drop support for IronPython for lack of ipy XML parsers
    * Migrate to pytest for unit testing (affects Python version support)
    * Drop support for Python 2.4, 2.5, 2.6, 3.0, 3.1, and 3.2
    * Add support for Python 3.6


0.18
----

*Released 21 April 2015*

    * Replace the regex RFC 822 date parser with procedural code


0.17
----

*Released 16 December 2012 -- "Territory expansion"*

    * Python 3.3 is now tested and supported!
    * PyPy is now tested and supported!
    * Jython 2.5.2 and 2.5.3 are now tested and supported!
    * Python 2 and 3 are now supported without 2to3 conversion
    * Remove the hack to work around Jython bug 1375
        (this means that Jython 2.5.1 is no longer supported)
    * Support single-digit days in RFC822 dates


0.16
----

*Released 17 December 2011 -- "Refresh"*

    * Python 3.2 is now supported!
    * Made setup.py auto-convert listparser using 2to3 if necessary
    * Switched to absolute URLs in the HTTP redirect tests


0.15
----

*Released 15 November 2010 "A special day"*

    * IronPython 2.6.2 is now supported!


0.14
----

*Released 22 October 2010 -- "A good year"*

    * Added support for LiveJournal FOAF files
    * Improved the documentation
    * Improved the code quality


0.13
----

*Released 1 February 2010 -- "Revelations"*

    * Fixed an infinite loop bug in Injector
    * Fixed a threading-related bug in the unit tests
    * Made Injector inject after the first '>', not '\n'
    * Overhauled and modularized the unit test code
    * Increased the code coverage of the unit tests


0.12
----

*Released 3 January 2010 -- "Safety net"*

    * Fixed global USER_AGENT behavior
    * Fixed several crasher bugs
    * Fixed a 2to3 tool warning in lptest.py
    * Made lptest.py return a status code to the shell


0.11
----

*Released 25 December 2009 -- "Floodgates"*

    * Jython 2.5.1 is now supported!
    * Added support for opening relative and absolute filenames


0.10
----

*Released 12 December 2009 -- "Internet-ready"*

    * Python 3 is now supported!
    * Correctly interpret undeclared HTML character entities
    * Significantly sped up large RDF+FOAF document parsing
    * Fixed RFC 822 date and time creation bug
    * Fixed RFC 822 crasher bugs
    * Fixed iGoogle-related crasher bug
    * Refreshed and added to documentation
    * Added many more tests


0.9
---

*Released 3 October 2009 -- "Celery wolves"*

    * Support RDF+FOAF!
    * Capture opportunity URLs
    * Added duplicate URL detection
    * Added distutils support for easier distribution


0.8
---

*Released 3 September 2009 -- "Three day weekend"*

    * Support the iGoogle exported settings format!
    * Support Liferea's version of subscription lists in OPML
    * Removed feeds[i].claims
    * Removed almost all of listparser's bozo warnings


0.7
---

*Released 28 August 2009 -- "The Codex"*

    * Added documentation!
    * Unified feed and subscription list code
    * Extended category and tag support to subscription lists
    * Result dictionary keys are now also attributes
        (i.e. result['meta']['title'] -> result.meta.title)
    * Feed and list titles are no longer filled with the
        associated URL if the title is not found


0.6
---

*Released 7 August 2009 -- "Hatchet Hotel"*

    * Certain return result elements are now guaranteed
    * `bozo_detail` has been renamed `bozo_exception`
    * Better support for Wordpress' wp-links-opml.php output
    * Added 22 new tests (and modified several others)


0.5
---

*Released 1 August 2009 -- "Going green"*

    * Send a (configurable) User-Agent header
    * Support HTTP ETag and Last-Modified headers
    * Support HTTP redirects and errors
    * Support parsing of strings and file-like objects (not just URLs)
    * The subscription list title is now stripped of whitespace
    * Added 11 more tests


0.4
---

*Released 18 July 2009 -- "07/18,29"*

    * Support categories and tags specified in @category
    * Support categorization using nested <outline> tags
    * Added 21 more tests


0.3
---

*Released 3 July 2009 -- "...and Recursion for all."*

    * The feed key `name` is now `title`
    * Additional optional attributes supported
    * Support subscription list inclusions
    * Added 13 more tests


0.2
---

*Released 26 June 2009 -- "Leveling up"*

    * RFC 822 date and time support added (+39 tests)
    * Added more thorough OPML version attribute detection (+5 tests)
    * `dateModified` and `dateCreated` OPML tags supported (+4 tests)
    * Added test cases for existing functionality (+2 tests)
    * <outline> `htmlUrl` attribute support added (+1 test)


0.1
---

*Released 19 June 2009 -- "Achievement unlocked"*

    * Initial release
