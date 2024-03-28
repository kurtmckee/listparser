import os
import pathlib
import sys

if sys.version_info[:2] >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

# Allow autodoc to import listparser.
sys.path.append(os.path.abspath("../src"))


# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ["sphinx.ext.autodoc"]

# The suffix of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "listparser"
copyright = "2009-2024 Kurt McKee"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
pyproject = pathlib.Path(__file__).parent.parent / "pyproject.toml"
info = tomllib.loads(pyproject.read_text())
version = release = info["tool"]["poetry"]["version"]

# List of directories, relative to source directory, that shouldn't be searched
# for source files.
exclude_trees = ()

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# HTML theme configuration
# ------------------------

html_theme = "alabaster"
