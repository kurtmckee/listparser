parse()
=======

.. py:currentmodule:: listparser

.. py:function:: parse(obj[, agent, etag, modified])

   Parse a subscription list and return a dictionary containing the results.

   :param obj: a file-like object or a string containing a URL, an absolute or relative filename, or an XML document
   :type obj: file or string
   :param agent: User-Agent header to be sent when requesting a URL
   :type agent: string
   :param etag: ETag header to be sent when requesting a URL
   :type etag: string
   :param modified: Last-Modified header to be sent when requesting a URL
   :type modified: string or datetime

   :return: all of the parsed information, webserver HTTP response headers, and any exception encountered
   :rtype: dictionary

   :py:func:`~listparser.parse` is the only public function exposed by listparser.   

   If *obj* is a URL, the :py:obj:`agent` will identify the software making the request, :py:obj:`etag` will identify the last HTTP ETag header returned by the webserver, and :py:obj:`modified` will identify the last HTTP Last-Modified header returned by the webserver. :py:obj:`agent` and :py:obj:`etag` must be strings, while :py:obj:`modified` can be either a string or a Python :py:class:`~datetime.datetime` object.

   If :py:obj:`agent` is not provided, the :py:data:`~listparser.USER_AGENT` global variable will be used by default.
