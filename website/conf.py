# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


# -- project information ---------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "WELL-PLAY-TEEN"
author = "Mathieu Scheltienne"
release = "0.0.1"
canonical_url = "https://well-play-teen.org/"

# -- general configuration -------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = "5.0"

# The document name of the “root” document, that is, the document that contains the root
# toctree directive.
root_doc = "index"

# Add any Sphinx extension module names here, as strings. They can be extensions coming
# with Sphinx (named "sphinx.ext.*") or your custom ones.
extensions = [
    "sphinxext.opengraph",
    "sphinx_copybutton",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

# Sphinx will warn about all references where the target cannot be found.
nitpicky = True
nitpick_ignore = []

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = []

# The name of a reST role (builtin or Sphinx extension) to use as the default role, that
# is, for text marked up `like this`. This can be set to 'py:obj' to make `filter` a
# cross-reference to the Python function “filter”.
default_role = "py:obj"

# -- options for HTML output -----------------------------------------------------------
html_context = {
    "canonical_url": canonical_url,
}
html_css_files = ["style.css"]
html_favicon = "_static/favicon.png"
html_logo = "_static/favicon.png"
html_permalinks_icon = "🔗"
html_show_sphinx = False
html_static_path = ["_static"]
html_theme = "insipid"
html_theme_options = {
    "breadcrumbs": False,
    "left_buttons": [],
    "nosidebar": True,
    "show_insipid": False,
}
html_title = project

# -- linkcheck -------------------------------------------------------------------------
linkcheck_anchors = False  # saves a bit of time
linkcheck_timeout = 15  # some can be quite slow
linkcheck_retries = 3
linkcheck_ignore = []  # will be compiled to regex

# -- sphinx opengraph ------------------------------------------------------------------
# use https://www.opengraph.xyz/ to preview the Open Graph data
ogp_site_url = canonical_url
ogp_image = canonical_url + "_static/header_lowres.jpg"
ogp_use_first_image = False
ogp_type = "website"
ogp_custom_meta_tags = [
    '<meta property="og:locale" content="fr_FR" />',
]
ogp_site_name = "Etude Well-Play Teen Genève"
