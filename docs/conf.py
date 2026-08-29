# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "FreeCAD NodeGraph Workbench"
copyright = "2025, FreeCAD Community"
author = "Jules"
release = "0.1.0"

# Offline build configuration: standard extensions without external network requirements
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.apidoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.graphviz",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Ensure offline build compatibility by avoiding external network fetches
intersphinx_mapping = {}
