FreeCAD NodeGraph Workbench Documentation
==========================================

Welcome to the official documentation for the **FreeCAD NodeGraph Workbench**.

The NodeGraph Workbench is a visual programming addon for `FreeCAD <https://www.freecad.org/>`_ that enables interactive parametric modeling using connected nodes.

Offline Documentation Building
------------------------------

Building local HTML documentation offline using Sphinx is the **primary method** for creating and viewing documentation in this project:

.. code-block:: bash

   pip install .[docs]
   sphinx-build -b html docs docs/_build/html

Open ``docs/_build/html/index.html`` to access full API reference guides, node library details, and code quality procedures offline. You can also view the automatically generated `Interactive HTML Code Coverage Report <coverage/index.html>`_.

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   usage
   nodes
   changelog

.. toctree::
   :maxdepth: 2
   :caption: Developer Reference

   api
   blender_architecture_analysis
   code_quality

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
