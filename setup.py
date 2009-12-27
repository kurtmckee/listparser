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
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Java',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing :: Markup :: XML',
    ]
)
