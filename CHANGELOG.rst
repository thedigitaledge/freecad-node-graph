=========
Changelog
=========

All notable changes to the FreeCAD NodeGraph Workbench project will be documented in this file.

Version 0.2.0 (2025-02-28)
--------------------------

Added
~~~~~
- FreeCAD Workbench scriptable function scanner and automatic dynamic node generator.
- Dynamic toolbars and action buttons for discovered workbenches (e.g. ``Part``, ``Draft``, ``Arch``, ``Mesh``).
- Parameter signature inspection to generate typed input sockets and output sockets for workbench functions.
- Unit tests for dynamic node generation and toolbar creation.

Version 0.1.0 (2025-02-28)
--------------------------

Added
~~~~~
- Initial release of the FreeCAD NodeGraph Workbench.
- Core node-graph data model: ``Socket``, ``Node``, ``Edge``, ``Graph``, and ``NodeRegistry``.
- Directed Acyclic Graph (DAG) topological evaluator with cycle detection.
- JSON serialization/deserialization for saving and loading graphs.
- Visual Nodes for CAD inputs (Float, Vector, Placement), primitives (Box, Cylinder, Sphere, Cone), booleans (Fuse, Cut, Common), features (Translate, Extrude, Compound), and Document Output.
- Qt/PySide graphical editor with node palette, property inspector, zoom/pan navigation, and graph control toolbar.
- FreeCAD Workbench integration via ``Init.py`` and ``InitGui.py``.
- Sphinx documentation with Read the Docs integration.
