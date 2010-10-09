etag
====

If an HTTP ETag header is received from the webserver, its exact text is stored in the ``etag`` key. It is strongly recommended that the ETag be stored and sent with every subsequent request in order to reduce bandwidth usage.

..  seealso:: :doc:`../http-features`

..  rubric:: Comes from

*   HTTP ETag header
