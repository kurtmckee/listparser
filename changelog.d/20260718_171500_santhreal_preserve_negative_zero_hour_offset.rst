Fixed
-----

*   Preserve the leading minus when parsing RFC 822 numeric timezones
    with a zero hour, such as ``-00:30`` and ``-0030``.
