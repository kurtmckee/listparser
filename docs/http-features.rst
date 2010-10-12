HTTP Features
=============

listparser supports several HTTP features, both to identify itself to webservers and to save bandwidth.


User-Agent
----------

listparser identifies itself to webservers by sending an HTTP User-Agent header. By default the header contains listparser's version, and a reference to the listparser homepage, but the header can be changed on a per-request basis or for all requests.

To change the User-Agent for only one request, call :py:func:`~listparser.parse` with an ``agent`` argument::

    >>> listparser.parse('http://localhost/list', agent='PowerfulSoftware/1.0')

To configure the User-Agent for all requests you need only set :py:data:`~listparser.USER_AGENT` to the desired value. The following code will send the same User-Agent header as the code above::

    >>> listparser.USER_AGENT = 'PowerfulSoftware/1.0'
    >>> listparser.parse('http://localhost/list')

If listparser is being used in a larger program it may be appropriate to change the User-Agent.

..  seealso:: :py:data:`~listparser.USER_AGENT`, `User agent at Wikipedia <http://en.wikipedia.org/wiki/User_agent>`_


ETag
----

When a webserver fulfills a request, it will often include an ETag header (the value of which may be a checksum of the file, such as its MD5 or SHA1 hash). listparser stores the value of the ETag header in the result's ``etag`` attribute::

    >>> result = listparser.parse('http://localhost/list')
    >>> result.etag
    '"ebe4f71184"'

If this value is passed in the ``etag`` argument to :py:func:`~listparser.parse`, the webserver will know whether the file has been modified since the last request. If it has been modified, the request will be fulfilled normally, and a new ETag header will be sent along with the file. If the file has not been modified, the webserver will return an HTTP 304 response in order to save bandwidth::

    >>> result = listparser.parse('http://localhost/list', etag='"ebe4f71184"')
    >>> result.status
    304

It is strongly recommended that software using listparser take advantage of the bandwidth-saving benefits of both the ETag and Last-Modified headers by checking for, storing, and sending both, as not all webservers support both.

..  seealso:: `HTTP Etag at Wikipedia <http://en.wikipedia.org/wiki/HTTP_ETag>`_


Last-Modified
-------------

In addition to the ETag header above, webservers often include a Last-Modified header, which represents the date and time at which a file was last updated. listparser stores the value of the Last-Modified header in the result's ``modified`` and ``modified_parsed`` attribute::

    >>> result = listparser.parse('http://localhost/list')
    >>> result.modified
    'Mon, 24 Aug 2009 21:10:01 GMT'
    >>> result.modified_parsed
    datetime.datetime(2009, 8, 24, 21, 10, 1)

If either of these values is passed to the ``modified`` argument of :py:func:`~listparser.parse`, the webserver will know whether to send the file or not. If the file has been modified, the request will be fulfilled normally and a new Last-Modified header will be sent. If not, the webserver will return an HTTP 304 response::

    >>> result = listparser.parse('http://localhost/list', modified='Mon, 24 Aug 2009 21:10:01 GMT')
    >>> result.status
    304

It is strongly recommended that software using listparser store and send both the Last-Modified and ETag headers, as not all webservers support both.
