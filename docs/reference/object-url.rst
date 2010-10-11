objects[i].url
==============

The URL of the feed, subscription list, or opportunity object. It is not normalized beyond the stripping of whitespace.

Due to the ubiquity of format-agnostic feed parsers, there is nothing to indicate what format the target feed is presented in.

..  rubric:: Feed URLs come from

*   ``/opml/body//outline/@xmlUrl``
*   ``/gtml:GadgetTabML//iGoogle:Module[@type="RSS"]/iGoogle:ModulePrefs/@xmlUrl``
*   ``/rdf:RDF//foaf:Agent//rss:channel/@rdf:about``
*   ``/rdf:RDF//ya:feed/@rdf:resource``


..  rubric:: Subscription list URLs come from

*   ``/opml/body//outline/@url``
*   ``/opml/body//outline[type="source"]/@xmlUrl``
*   ``/rdf:RDF//rdfs:seeAlso/@rdf:resource``


..  rubric:: Opportunity URLs come from

*   ``/opml/body//outline/@htmlUrl``
*   ``/rdf:RDF//foaf:Agent//foaf:Document/@rdf:about``

