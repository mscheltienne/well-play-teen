# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from datetime import date

# -- project information ---------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "WELL-PLAY-TEEN"
author = "Mathieu Scheltienne"
copyright = f"{date.today().year}, {author}"  # noqa: A001
release = "0.0.2"
canonical_url = "https://well-play-teen.org/"
description = (
    "L'Université et la Haute Ecole de Santé de Genève vous proposent de vous inscrire "
    "pour participer à un projet de recherche sur l'impact des jeux vidéos sur la "
    "santé et les émotions des adolescents."
)

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
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.mathjax",
    "sphinxext.opengraph",
    "sphinxcontrib.bibtex",
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
    "default_mode": "light",
}
html_css_files = ["style.css"]
html_favicon = "_static/logo.png"
html_logo = "_static/logos.png"
html_permalinks_icon = "🔗"
html_sidebars = {"**": []}
html_show_sphinx = False
html_static_path = ["_static"]
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "article_header_start": [],
    "external_links": [
        {
            "name": "Brain and Learning lab",
            "url": "https://www.unige.ch/fapse/brainlearning",
        },
        {
            "name": "Daphne Bavelier",
            "url": "https://www.unige.ch/cisa/center/members/bavelier-daphne/",
        },
        {
            "name": "Swann Pichon",
            "url": "https://www.hesge.ch/heds/la-heds/annuaire/swann-pichon",
        },
    ],
    "footer_end": [],
    "header_links_before_dropdown": 3,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/mscheltienne/well-play-teen",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
    ],
    "navbar_persistent": ["participate"],
    "navbar_end": ["navbar-icon-links"],
    "navigation_with_keys": False,
    "use_edit_page_button": False,
    "secondary_sidebar_items": [],
    "show_prev_next": False,
}
html_title = project

# -- autosectionlabels -----------------------------------------------------------------
autosectionlabel_prefix_document = True

# -- sphinxcontrib-bibtex --------------------------------------------------------------
bibtex_bibfiles = ["./references.bib"]

# -- linkcheck -------------------------------------------------------------------------
linkcheck_anchors = False  # saves a bit of time
linkcheck_timeout = 15  # some can be quite slow
linkcheck_retries = 3
linkcheck_ignore = []  # will be compiled to regex

# -- sphinx_copybutton -----------------------------------------------------------------
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# -- sphinx opengraph ------------------------------------------------------------------
# use https://www.opengraph.xyz/ to preview the Open Graph data
ogp_site_url = canonical_url
ogp_enable_meta_description = False
ogp_custom_meta_tags = [
    '<meta property="og:title" content="Participez à Well-Play !">',
    f'<meta property="og:description" content="{description}">',
    f'<meta name="description" content="{description}">',
]
