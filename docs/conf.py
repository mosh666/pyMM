"""Sphinx configuration file for pyMediaManager documentation."""

from datetime import UTC, datetime
import os
from pathlib import Path
import sys

# Add project root to Python path for autodoc
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set environment variable to prevent PySide6 import issues during doc build
os.environ["QT_QPA_PLATFORM"] = "offscreen"

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
    "sphinx.ext.inheritance_diagram",  # Generate inheritance diagrams
    "myst_parser",  # Support for Markdown files
    "sphinx_multiversion",  # Support for multiple versions
    "sphinx_copybutton",  # Add copy button to code blocks
    "sphinx_tabs.tabs",  # Support for tabbed content
    "sphinx_design",  # Modern design components (cards, grids, badges)
    "notfound.extension",  # Custom 404 page
    "sphinxcontrib.mermaid",  # Mermaid diagram support
    "sphinxcontrib.spelling",  # Spell checking
    "sphinxcontrib.redirects",  # URL redirects from old structure
]

# Add any paths that contain templates here
templates_path = ["_templates"]

# Whitelist pattern for branches - build docs for main and dev
smv_branch_whitelist = r"^(main|dev)$"
smv_remote_whitelist = r"^origin$"
# Include beta versions in documentation (v0.1.0, v0.1.0-beta.1, v1.0.0, etc.)
smv_tag_whitelist = r"^v\d+\.\d+\.\d+(-beta\.\d+)?$"
# Latest version displayed in version selector
smv_latest_version = "main"
# Prefer remote branches over local
smv_prefer_remote_refs = True

# List of patterns, relative to source directory, to ignore when looking for source files
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Suppress warnings for autodoc import failures (PySide6 introspection issues)
suppress_warnings = [
    "autodoc",
    "autodoc.import_object",
]

# The suffix(es) of source filenames
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# MyST Parser configuration for Markdown
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "attrs_inline",
    "attrs_block",
]

# The master toctree document
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages
html_theme = "furo"

# Theme options for Furo
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#4CAF50",
        "color-brand-content": "#212121",
        "font-stack": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        "font-stack--monospace": "'Consolas', 'Monaco', 'Courier New', monospace",
    },
    "dark_css_variables": {
        "color-brand-primary": "#66BB6A",
        "color-brand-content": "#E0E0E0",
    },
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
    # Source repository for "Edit on GitHub" links
    "source_repository": "https://github.com/mosh666/pyMM",
    "source_branch": "main",
    "source_directory": "docs/",
    # Announcement for dev branch warning (will be conditionally set)
    "announcement": None,  # Set dynamically for dev branch
}

# Add any paths that contain custom static files (such as style sheets)
html_static_path = ["_static"]

# Custom CSS files
html_css_files = [
    "custom.css",
]

# Custom sidebar templates, maps document names to template names
html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "versioning.html",  # Version selector
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/ethical-ads.html",
        "sidebar/scroll-end.html",
        "sidebar/variant-selector.html",
    ]
}

# SEO and metadata
html_meta = {
    "description": "Comprehensive documentation for pyMediaManager - Portable Python-based media management application with PySide6 Fluent UI, cross-platform drive detection, and extensible plugin system for Windows, Linux, and macOS.",
    "keywords": "media management, portable, digikam, pyside6, fluent ui, plugin system, documentation, cross-platform, windows, linux, macos",
    "author": "mosh666",
    "og:site_name": "pyMediaManager Documentation",
    "og:type": "website",
    "og:url": "https://mosh666.github.io/pyMM/",
    "og:title": "pyMediaManager - Portable Cross-Platform Media Management",
    "og:description": "Professional-grade media management application with modern Fluent UI, extensible plugin system, and unified drive detection across Windows, Linux, and macOS. 100% portable, runs from USB drives with zero system footprint.",
    "twitter:card": "summary_large_image",
    "twitter:title": "pyMediaManager - Portable Media Management",
    "twitter:description": "Cross-platform media management with PySide6 Fluent UI, plugin system, and professional tools for Windows, Linux, and macOS.",
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

# -- Options for sphinx-copybutton -------------------------------------------

# Button text and behavior
copybutton_prompt_text = r">>> |\.\.\. |\$ |PS> "
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = True
copybutton_remove_prompts = True

# -- Options for sphinx-tabs -------------------------------------------------

# Synchronize tab selections across pages
sphinx_tabs_valid_builders = ["html", "linkcheck"]
sphinx_tabs_disable_tab_closing = True

# -- Options for sphinxcontrib-mermaid ---------------------------------------

# Mermaid diagram configuration
mermaid_version = "10.6.1"
mermaid_init_js = """
mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    securityLevel: 'loose',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
});
"""

# -- Options for sphinxcontrib-spelling --------------------------------------

# Spell checking configuration
spelling_lang = "en_US"
spelling_word_list_filename = "spelling_wordlist.txt"
spelling_show_suggestions = True
spelling_exclude_patterns = ["api-reference.md", "_build/*"]

# -- Options for sphinx-notfound-page ----------------------------------------

# Custom 404 page configuration
notfound_context = {
    "title": "Page Not Found",
    "body": """
    <h1>404 - Page Not Found</h1>
    <p>The page you're looking for doesn't exist. This might be because:</p>
    <ul>
        <li>The URL has changed after the documentation redesign</li>
        <li>The page has been moved or removed</li>
        <li>You followed an outdated link</li>
    </ul>
    <p>Try using the search function or browse the navigation menu.</p>
    """,
}
notfound_urls_prefix = "/pyMM/"

# -- Options for sphinxcontrib-redirects -------------------------------------

# URL redirects from old sphinx_rtd_theme structure to new Furo structure
# Format: {old_url: new_url}
redirects = {
    # Redirect old RTD-style URLs to new Furo structure
    "getting-started.html": "user-guide.html",
    "installation.html": "user-guide.html#installation",
    "configuration.html": "user-guide.html#configuration",
    "api.html": "api-reference.html",
    "plugins.html": "plugin-development.html",
    "contributing.html": "../CONTRIBUTING.md",
    # Add more redirects as needed
}

# -- Options for sphinx-multiversion compatibility ---------------------------

# Check if building with sphinx-multiversion and set dev branch warning
try:
    import os

    smv_current = os.environ.get("SPHINX_MULTIVERSION_NAME", "")

    if smv_current == "dev":
        html_theme_options["announcement"] = (
            "⚠️ <strong>Development Branch</strong> — "
            "You are viewing documentation for the development version. "
            "Features may be incomplete or subject to change. "
            'For stable documentation, view the <a href="../main/index.html" style="color: #4CAF50; font-weight: bold;">main branch</a>.'
        )
    elif smv_current.startswith("v") and "-beta" in smv_current:
        html_theme_options["announcement"] = (
            "🧪 <strong>Beta Version</strong> — "
            f"You are viewing documentation for {smv_current}. "
            'For stable documentation, view the <a href="../main/index.html" style="color: #4CAF50; font-weight: bold;">main branch</a>.'
        )
except Exception:  # noqa: BLE001
    pass

# -- Options for inheritance diagrams ----------------------------------------

# Inheritance diagram configuration
inheritance_graph_attrs = {
    "rankdir": "LR",
    "size": '"8.0, 10.0"',
    "fontsize": 14,
    "ratio": "compress",
}

inheritance_node_attrs = {
    "shape": "box",
    "fontsize": 14,
    "height": 0.75,
    "color": '"#4CAF50"',
    "style": '"rounded,filled"',
    "fillcolor": '"#E8F5E9"',
}


# Setup function to configure autodoc behavior
def setup(app):
    """Configure Sphinx application."""

    # Skip autodoc for modules that have PySide6 import issues
    def skip_pyside_imports(_app, what, _name, obj, skip, _options):
        """Skip autodoc for classes/modules with PySide6 import issues."""
        # Skip UI components that fail to import
        if what in ("class", "module"):
            problematic_modules = [
                "app.ui.components.first_run_wizard",
                "app.ui.views.plugin_view",
                "app.ui.views.project_view",
                "app.ui.views.storage_view",
                "app.ui.main_window",
                "app.ui.dialogs",
            ]
            module_name = getattr(obj, "__module__", "")
            if any(mod in module_name for mod in problematic_modules):
                return True
        return skip

    app.connect("autodoc-skip-member", skip_pyside_imports)
