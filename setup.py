from setuptools import setup

setup(
    name='listparser',
    version='0.18',
    description='Parse OPML, FOAF, and iGoogle subscription lists.',
    long_description="""listparser is a Python library that parses subscription lists (also called reading lists) and returns all of the feeds, subscription lists, and "opportunity" URLs that it finds. It supports OPML, RDF+FOAF, and the iGoogle exported settings format.""",
    author='Kurt McKee',
    author_email='contactme@kurtmckee.org',
    url='https://github.com/kurtmckee/listparser',
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: Jython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing :: Markup :: XML',
    ]
)
