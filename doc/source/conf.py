"""Sphinx configuration file for icclim documentation."""  # noqa: INP001
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import sys
from pathlib import Path

sys.path.insert(0, Path("../..").resolve())
import icclim  # (import need to be after path update)

# -- Project information -----------------------------------------------------
project = "icclim"
copyright = "2021, CERFACS"  # noqa: A001
author = "Christian P."
version = icclim.__version__
release = icclim.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # Finds sources from object description and generated highlighted standalone pages
    "sphinx.ext.viewcode",
    # Enables parsing of numpy's style docstring
    "sphinx.ext.napoleon",
    # Allows to link to external ressources
    "sphinx.ext.intersphinx",
    # Makes code example clickable
    "sphinx_codeautolink",
    # make sphinx extension fetch LFS content
    "sphinx_lfs_content",
    # Add copy button to code snippets
    "sphinx_copybutton",
    # Add ipython directive
    "IPython.sphinxext.ipython_console_highlighting",
    "IPython.sphinxext.ipython_directive",
    # Add notebook parsing
    "nbsphinx",
    # Enable autoapi directives
    "sphinx.ext.autodoc",
    "autoapi.extension",
]
autoapi_generate_api_docs = False
autoapi_dirs = ["../../src"]
autoapi_root = "references/api"
# autoapi_keep_files = True   # noqa: ERA001 , E501 (uncomment to generate the API and recomment after)
autoapi_options = [
    # "members",
    # "undoc-members",
    "private-members",
    # "show-inheritance",
    # "show-module-summary",
    # "special-members",
    "imported-members",
]

autosectionlabel_maxdepth = 2

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

html_favicon = "_static/logo_icclim_favicon__displayed.ico"
html_theme_options = {
    "logo": {
        "image_light": "logo_icclim_colored__displayed.svg",
        "image_dark": "logo_icclim_white__displayed.svg",
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/cerfacs-globc/icclim",  # required
            "icon": "fab fa-github-square",
            "type": "fontawesome",
        },
    ],
}

intersphinx_mapping = {
    "clisops": ("https://clisops.readthedocs.io/en/latest/", None),
    "flox": ("https://flox.readthedocs.io/en/latest/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "sklearn": ("https://scikit-learn.org/stable/", None),
    "statsmodels": ("https://www.statsmodels.org/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "xclim": ("https://xclim.readthedocs.io/en/stable/", None),
}

# The master toctree document.
master_doc = "index"
