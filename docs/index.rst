pyMediaManager Documentation
============================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   user-guide
   architecture
   plugin-development
   contributing
   changelog
   api/index

Welcome to pyMediaManager
=========================

pyMediaManager (pyMM) is a Python-based media management application designed to organize and manage large media collections with integrated version control and plugin support.

Features
--------

- **Project Management**: Organize media files into structured projects
- **Storage Management**: Configure and manage multiple storage locations
- **Plugin System**: Extensible architecture for integrating external tools
- **Git Integration**: Built-in version control support
- **Cross-platform**: Windows support with portable external tools

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/mosh666/pyMM.git
   cd pyMM
   pip install -e .

Running the Application
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python launcher.py

Or use the installed entry point:

.. code-block:: bash

   pymm

Documentation Sections
----------------------

* :doc:`user-guide` - End-user guide for using pyMediaManager
* :doc:`architecture` - Technical architecture and design decisions
* :doc:`plugin-development` - Guide for developing plugins
* :doc:`api/index` - Complete API reference

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
