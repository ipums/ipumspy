# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

import doctest
import inspect
import logging as pylogging

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import shutil
import subprocess
import sys

from sphinx.util import logging

sys.path.append(os.path.abspath("../../src"))
import ipumspy

sys.path.insert(0, os.path.abspath("../../src/ipumspy"))


# -- Project information -----------------------------------------------------

project = "ipumspy"
copyright = "2021, Regents of the University of Minnesota"
author = "Kevin H. Wilson, Edward Huh, Renae Rodgers"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.doctest",
    "sphinx.ext.napoleon",  # N.B. napoleon must be before autodocs_typehints
    "sphinx_autodoc_typehints",
    "sphinx.ext.linkcode",  # link to github, see linkcode_resolve() below
    "sphinx_copybutton",
    "myst_parser",
]

doctest_global_setup = """
import sys
import pandas as pd
import numpy as np
from packaging import version
pd.options.display.max_columns = None # For Travis on macOS
pd.options.display.max_rows = None # For Travis on macOS

try:
    import hypothesis
except ImportError:
    SKIP_STRATEGY = True
else:
    SKIP_STRATEGY = False

SKIP = sys.version_info < (3, 6)
PY36 = sys.version_info < (3, 7)
SKIP_PANDAS_LT_V1 = version.parse(pd.__version__).release < (1, 0) or PY36
SKIP_SCALING = True
"""

doctest_default_flags = (
    0
    | doctest.DONT_ACCEPT_TRUE_FOR_1
    | doctest.ELLIPSIS
    | doctest.IGNORE_EXCEPTION_DETAIL
    | doctest.NORMALIZE_WHITESPACE
)

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# copy CONTRIBUTING.md docs into source directory
root_dir = os.path.dirname(__file__)
shutil.copyfile(
    os.path.join(root_dir, "..", "..", "CONTRIBUTING.md"),
    os.path.join(root_dir, "CONTRIBUTING.md"),
)

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The master toctree document.
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

autoclass_content = "both"

autodoc_default_options = {
    "undoc-members": False,
}

# -- Options for HTML output -------------------------------------------------

html_title = "ipumspy"

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
pygments_style = "friendly"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

html_logo = "_static/ipumspy-logo.png"
html_favicon = "_static/ipums-favicon-152x152.png"
html_theme_options = {
    "light_css_variables": {
        # not official IPUMS color
        "color-brand-primary": "#3280A9",
        "color-brand-content": "#3280A9",
        # IPUMS light grey
        "color-api-highlight-on-target": "#F1F5F7",
    },
    # always use light theme, taken from:
    # https://github.com/pradyunsg/furo/blob/main/src/furo/assets/styles/variables/_index.scss
    "dark_css_variables": {
        "color-foreground-primary": "black",
        # IPUMS Navy
        "color-foreground-secondary": "#00263A",
        # IPUMS blue grey
        "color-foreground-muted": "#7A99AC",
        "color-foreground-border": "#878787",
        "color-background-primary": "white",
        # IPUMS near white
        "color-background-secondary": "#FBFCFC",
        "color-background-hover": "#efeff4ff",
        "color-background-hover--transparent": "#efeff400",
        "color-background-border": "#eeebee",
        "color-admonition-background": "transparent",
        # IPUMS light grey
        "color-api-highlight-on-target": "#F1F5F7",
    },
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = ["default.css"]

rst_prolog = """
.. role:: red
.. role:: green
"""

autosummary_generate = True
autosummary_filename_map = {}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://docs.scipy.org/doc/numpy/", None),
    "pandas": ("http://pandas.pydata.org/pandas-docs/stable/", None),
}

# strip prompts
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True


# this is a workaround to filter out forward reference issue in
# sphinx_autodoc_typehints
class FilterPandasTypeAnnotationWarning(pylogging.Filter):
    def filter(self, record: pylogging.LogRecord) -> bool:
        # You probably should make this check more specific by checking
        # that dataclass name is in the message, so that you don't filter out
        # other meaningful warnings
        return not record.getMessage().startswith(
            "Cannot resolve forward reference in type annotations of "
            '"pandera.typing.DataFrame"'
        )


logging.getLogger("sphinx_autodoc_typehints").logger.addFilter(
    FilterPandasTypeAnnotationWarning()
)


# based on pandas/doc/source/conf.py
def linkcode_resolve(domain, info):
    """Determine the URL corresponding to Python object."""
    if domain != "py":
        return None

    submod = sys.modules.get(info["module"])
    if submod is None:
        return None

    obj = submod
    for part in info["fullname"].split("."):
        try:
            obj = getattr(obj, part)
        except AttributeError:
            return None

    try:
        fn = inspect.getsourcefile(inspect.unwrap(obj))
    except TypeError:
        fn = None
    if not fn:
        return None

    try:
        source, lineno = inspect.getsourcelines(obj)
    except OSError:
        lineno = None

    fn = os.path.relpath(fn, start=os.path.dirname(ipumspy.__file__))

    linespec = f"#L{lineno}-L{lineno + len(source) - 1}" if lineno else ""

    try:  # check if we are building "latest" version on reathedocs
        tag = (
            subprocess.check_output(["git", "branch", "--show-current"])
            .decode("utf-8")
            .strip()
        )
    except subprocess.CalledProcessError:
        tag = None

    if tag != "master":
        tag = f"v{ipumspy.__version__}"

    return f"https://github.com/ipums/ipumspy/blob/{tag}/src/ipumspy/{fn}{linespec}"
