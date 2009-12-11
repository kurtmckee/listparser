feeds[i].url
============

The URL of the feed. Due to the ubiquity of format-agnostic feed parsers, there is nothing to indicate what format the target feed is presented in. It is not normalized beyond the stripping of whitespace.

..  rubric:: Comes from

*   ``/opml/body//outline/@xmlUrl``
*   ``/gtml:GadgetTabML//iGoogle:Module[@type="RSS"]/iGoogle:ModulePrefs/@xmlUrl``
*   ``/rdf:RDF//foaf:Agent//rss:channel/@rdf:about``
