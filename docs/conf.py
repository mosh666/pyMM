"""Sphinx configuration file for pyMediaManager documentation."""

from datetime import UTC, datetime
from pathlib import Path
import sys

# Add project root to Python path for autodoc
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# -- Project information -----------------------------------------------------
project = "pyMediaManager"
project_copyright = f"2024-{datetime.now(tz=UTC).year}, mosh666"
author = "mosh666"

# The full version, including alpha/beta/rc tags
# For sphinx-multiversion: Use a simple fallback since the package isn't installed
# in the temp git checkouts. The actual version will be set by sphinx-multiversion
# from git tags.
release = "latest"
version = "latest"

# Try to get the actual version if available (when building from installed package)
try:
    from importlib.metadata import version as get_version

    release = get_version("pyMediaManager")
    version = release
except Exception:  # noqa: BLE001
    # In sphinx-multiversion temp checkouts, we can't get the version from the package
    # The version will be available via smv_current_version at build time
    pass

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here
extensions = [
    "sphinx.ext.autodoc",  # Auto-generate documentation from docstrings
    "sphinx.ext.napoleon",  # Support for Google-style docstrings
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.intersphinx",  # Link to other projects' documentation
    "sphinx.ext.todo",  # Support for TODO items
    "sphinx.ext.coverage",  # Coverage checker for documentation
    "sphinx.ext.githubpages",  # Generate .nojekyll file for GitHub Pages
    "myst_parser",  # Support for Markdown files
    "sphinx_multiversion",  # Support for multiple versions
]

# Add any paths that contain templates here
templates_path = ["_templates"]

# Whitelist pattern for branches (set to None to ignore all branches)
smv_branch_whitelist = r"^(main|dev)$"
smv_remote_whitelist = r"^origin$"
smv_tag_whitelist = r"^v\d+\.\d+.*$"

# List of patterns, relative to source directory, to ignore when looking for source files
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The suffix(es) of source filenames
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# MyST Parser configuration for Markdown
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

# The master toctree document
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages
html_theme = "sphinx_rtd_theme"

# Theme options
html_theme_options = {
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

# Add any paths that contain custom static files (such as style sheets)
html_static_path = ["_static"]

# Custom sidebar templates, maps document names to template names
html_sidebars = {
    "**": [
        "globaltoc.html",
        "relations.html",
        "sourcelink.html",
        "searchbox.html",
        "versioning.html",
    ]
}

# Output file base name for HTML help builder
htmlhelp_basename = "pyMediaManagerdoc"

# -- Options for autodoc -----------------------------------------------------

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "show-inheritance": True,
}

autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
autodoc_class_signature = "separated"

# Mock imports for external dependencies that may not be installed
autodoc_mock_imports = [
    "PySide6",
    "qfluentwidgets",
    "yaml",
    "psutil",
    "aiofiles",
]

# -- Options for Napoleon (Google-style docstrings) -------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for intersphinx -------------------------------------------------

# Links to external documentation
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pyside6": ("https://doc.qt.io/qtforpython-6/", None),
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing
todo_include_todos = True
