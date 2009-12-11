Feed and subscription list detection algorithm
==============================================

..  note::

    Neither RDF+FOAF nor the iGoogle exported settings formats support embedded subscription lists. This detection algorithm only applies to OPML subscription lists.

Many services and softwares output OPML subscription lists with slight variations. listparser attempts to correctly determine whether an ``outline`` element is attempting to reference a feed or subscription list. As an example, although feeds should be indicated using ``type="rss"`` (no matter the format), some services refer to feeds using ``type="link"``, others indicate that the feed is Atom-formatted using ``type="pie"``, and still others fail to include a ``type`` attribute at all! Therefore it is necessary to make educated guesses.


Feed detection
--------------

If the ``outline`` element contains an ``xmlUrl`` attribute, the ``outline`` is assumed to represent a feed. listparser will also accept ``xmlurl``, or ``xmlURL``, or indeed any capitalization combination.

The ``type`` is ignored entirely in making the decision, with one notable exception (see below).


Subscription list detection
---------------------------

If the ``outline`` element has a ``url`` attribute and ``type="link"`` or ``type="include"``, listparser assumes that it has found a subscription list. Additionally, if it has an ``xmlUrl`` attribute and ``type="source"``, it is also considered a subscription list.

Although the "include" value was only introduced in OPML 2.0, listparser ignores the OPML version entirely. Additionally, despite the OPML 2.0 requirement that the ``url`` value of "link" ``outline`` elements must end in ".opml" to be considered an OPML file, listparser ignores the URL suffix when detecting whether the element is a subscription list.
