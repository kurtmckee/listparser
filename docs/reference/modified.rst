modified
========

A string returned by the webserver representing the date and time at which the subscription list was last modified. The string should be in RFC 2822 format.

..  note::

    ``modified`` represents the date and time at which the **webserver** claims the file was last updated. ``meta.modified`` represents the date and time at which the **subscription list** claims to have last been updated.

..  seealso::

    * :doc:`modified_parsed`
    * :doc:`meta-modified`
    * :doc:`../http-features`

..  rubric:: Comes from

*   HTTP Last-Modified header
