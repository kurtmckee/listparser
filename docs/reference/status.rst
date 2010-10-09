status
======

An integer representing the HTTP status returned by the webserver. [#codes]_

This value can be used to determine whether the location of the subscription list is still valid, or if it should be updated. For instance, if ``status == 301``, the subscription list has been "Moved Permanently", and the new location should be used for future requests.

..  seealso:: :doc:`href`

..  rubric:: Footnotes

..  [#codes] `List of HTTP status codes <http://en.wikipedia.org/wiki/List_of_HTTP_status_codes>`_

