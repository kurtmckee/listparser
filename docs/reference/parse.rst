parse()
=======

.. function:: parse(object_to_parse[, agent=USER_AGENT][, etag=None][, modified=None])

   The :func:`parse` function is the only public function exposed by listparser. The *object_to_parse* must be a file-like object or a string containing a URL, a filename, or an XML document.
   
   If *object_to_parse* is a URL, *agent* will identify the software making the request, *etag* will identify the last HTTP ETag header returned by the webserver, and *modified* will identify the last HTTP Last-Modified header returned by the webserver. *agent* and *etag* must be strings, while *modified* can be either a string or a Python ``datetime`` object.
