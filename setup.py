from setuptools import setup

# Convert the long description from a paragraph to a single line.
long_description = """
listparser is a Python library that parses subscription lists
(also called reading lists) and returns all of the feeds,
subscription lists, and "opportunity" URLs that it finds.
It supports OPML, RDF+FOAF, and the iGoogle exported settings format.
"""
long_description = ' '.join(long_description.strip().splitlines())

setup(
    name='listparser',
    version='0.18',
    description='Parse OPML, FOAF, and iGoogle subscription lists.',
    long_description=long_description,
    author='Kurt McKee',
    author_email='contactme@kurtmckee.org',
    url='https://github.com/kurtmckee/listparser',
    packages=['listparser'],
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',  # noqa: E501
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing :: Markup :: XML',
    ]
)
