from distutils.core import setup

from listparser import __version__

setup(
    name='listparser',
    version=__version__,
    description='Parse subscription lists into a consistent format.',
    long_description="""
        listparser is a Python library that parses subscription lists (also
        called reading lists) and returns all of the feeds and subscription
        lists that it finds. It currently supports OPML and the iGoogle
        exported settings format.
    """,
    author='Kurt McKee',
    author_email='contactme@kurtmckee.org',
    url='http://freshmeat.net/projects/listparser',
    py_modules=['listparser'],
)
