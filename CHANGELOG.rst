=========
Changelog
=========

All notable changes to the FreeCAD NodeGraph Workbench project will be documented in this file.

Version 0.14.0 (2025-02-28)
---------------------------

Changed
~~~~~~~
- Removed forced TaskPanel focus upon NodeGraph object creation so creating objects in the Model tree view remains clean.

Version 0.13.0 (2025-02-28)
---------------------------

Changed
~~~~~~~
- Moved Node Library palette and Properties Inspector to FreeCAD's Tasks overlay panel using FreeCAD's TaskPanel system (``NodeGraphTaskPanel``).
- Updated ``CommandCreateNodeGraphObject`` and ``make_nodegraph_object`` to nest newly created NodeGraph objects as children under selected parent objects in the Model tree view.

Version 0.12.0 (2025-02-28)
---------------------------

Changed
~~~~~~~
- Moved the Node Library palette and Properties Inspector into a right-side overlay panel on the NodeGraph editor window.
- Updated auto-generated object names and window titles to format as ``NodeGraph:X`` (e.g. ``NodeGraph:1``, ``NodeGraph:2``), removing the ``NodeGraph Editor -`` title prefix.
- Removed auto-focusing on the Tasks view tab when selecting the editor.

Version 0.11.0 (2025-02-28)
---------------------------

Added
~~~~~
- Per-object document graph data storage: creating a NodeGraph document object initializes an independent graph storage saved in the document's ``GraphData`` property.
- Bound editor windows: opening a NodeGraph object loads and edits exclusively that object's graph data, automatically auto-saving edits to the document object.
- Unit tests verifying isolated graph data storage across multiple document objects.

Version 0.10.0 (2025-02-28)
---------------------------

Added
~~~~~
- FreeCAD selection observer (``NodeGraphSelectionObserver``) listening for NodeGraph object selections in the Model tree view to automatically open and display the NodeGraph editor window and Tasks panel.

Version 0.9.0 (2025-02-28)
--------------------------

Added
~~~~~
- FeaturePython ``NodeGraphObject`` (and ``ViewProviderNodeGraph``) allowing creation of parametric NodeGraph objects directly in FreeCAD's Model tree view.
- Support for adding NodeGraph objects both at the top level of a document or nested inside subobjects, bodies, and groups.
- Automatic recomputation of ``NodeGraphObject.Shape`` when FreeCAD document recomputes.
- Command ``NodeGraph_CreateObject`` in workbench toolbar and menu.

Version 0.8.0 (2025-02-28)
--------------------------

Changed
~~~~~~~
- Moved the Node Library palette and Properties Inspector into FreeCAD's **Tasks** view using FreeCAD's TaskPanel system (``NodeGraphTaskPanel``).
- Integrated automatic dialog display so opening or focusing the NodeGraph editor view displays the Node Library directly in the Tasks view.

Version 0.7.0 (2025-02-28)
--------------------------

Added
~~~~~
- Automatic Node Library tab focus: selecting or activating the NodeGraph editor view automatically switches the active ComboView tab to "Node Library".
- Unit test suite verifying automatic Node Library tab switching on editor activation.

Version 0.6.0 (2025-02-28)
--------------------------

Changed
~~~~~~~
- Refactored Node Graph view window into a main workspace MDI subwindow view (matching FreeCAD Spreadsheet view style) and removed top toolbars per design request.
- Moved the side panel containing the Node Library palette and Properties Inspector into a dedicated tab in FreeCAD's ComboView / Task panel (alongside "Model" and "Tasks").
- Added a real-time search filter input field to the Node Library panel for instantly filtering nodes by name.

Version 0.5.0 (2025-02-28)
--------------------------

Changed
~~~~~~~
- Embedded the Node Graph visual editor directly into FreeCAD's main window as a dock panel view (``QDockWidget``) instead of opening in a separate floating window.
- Updated ``NodeGraphEditorWidget`` architecture for seamless dock integration within FreeCAD.

Version 0.4.0 (2025-02-28)
--------------------------

Added
~~~~~
- Secondary click (right-click) context menu on graph nodes providing **Cut**, **Copy**, **Paste**, **Duplicate**, and **Detach Links** actions.
- Internal scene clipboard logic for copying and pasting subgraphs.
- Detach links function removing all input and output connection edges from a node.

Version 0.3.0 (2025-02-28)
--------------------------

Added
~~~~~
- Clear text labels displaying input and output socket names directly on canvas node items.
- Distinct data-type color coding for input and output sockets (Float, Int, String, Boolean, Vector, Placement, Shape, Object, Any).
- Dynamic edge colors matching the output socket data type.

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
