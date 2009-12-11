headers
=======

The ``headers`` key is a dictionary of all of the headers returned by a webserver if a subscription list is requested from a URL.

Developers should be aware that Python 2 normalizes all header names, while Python 3 does not. Thus, if the webserver sends an ``X-Bender`` header, its Python 2 name will be ``x-bender``, while its Python 3 name will be unchanged.
