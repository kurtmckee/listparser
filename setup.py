from distutils.core import setup

from listparser import __version__

setup(
    name='listparser',
    version=__version__,
    description='Parse subscription lists into a consistent format.',
    long_description="""listparser is a Python library that parses subscription lists (also called reading lists) and returns all of the feeds, subscription lists, and "opportunity" URLs that it finds. It supports OPML, RDF+FOAF, and the iGoogle exported settings format.""",
    author='Kurt McKee',
    author_email='contactme@kurtmckee.org',
    url='http://freshmeat.net/projects/listparser',
    py_modules=['listparser'],
)
