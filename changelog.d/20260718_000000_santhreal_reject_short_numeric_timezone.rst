Fixed
-----

*   Reject short numeric RFC 822 timezones like ``+050`` instead of
    misparsing them as a ``+00:50`` offset.
