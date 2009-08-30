modified
========

A string returned by the webserver representing the date and time at which the subscription list was last modified. The string should be in RFC 2822 format.

..  note::

    ``modified`` represents the date and time at which the **server** claims the file was last updated. ``meta.modified`` represents the date and time at which the **subscription list** claims to have last been updated.

..  seealso::

    * `modified_parsed <modified_parsed.html>`_
    * `meta.modified <meta-modified.html>`_
    * `HTTP Features <../http-features.html>`_

..  rubric:: Comes from

*   HTTP Last-Modified header