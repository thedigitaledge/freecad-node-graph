FreeCAD NodeGraph Workbench
===========================

.. image:: https://readthedocs.org/projects/freecad-nodegraph/badge/?version=latest
   :target: https://freecad-nodegraph.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

**FreeCAD NodeGraph Workbench** is a visual programming extension for `FreeCAD <https://www.freecad.org/>`_ that enables parametric modeling and CAD feature programming through a node-graph visual scripting interface.

Features
--------

- **Node Library in FreeCAD Tasks View**: Displays the Node Library palette and Properties Inspector inside FreeCAD's **Tasks** view overlay panel using FreeCAD's TaskPanel system.
- **Parent-Child Object Nesting**: Creating a new NodeGraph object while another object is selected in the Model tree view automatically adds the NodeGraph object as a child of the selected parent object.
- **NodeGraph:X Auto-Naming**: Automatically names new document objects ``NodeGraph:1``, ``NodeGraph:2``, etc., and displays ``NodeGraph:X`` directly as the window title.
- **Per-Object Document Data Storage**: Creating a NodeGraph object creates an independent graph data storage saved directly inside the FreeCAD document. Opening the editor loads and edits exclusively that object's graph data.
- **Automatic Selection Display**: Selecting any NodeGraph object in FreeCAD's Model tree view automatically opens and displays its NodeGraph editor workspace view.
- **FreeCAD MDI Main View (Spreadsheet Style)**: Opens the node graph editor directly as a main document tab view in FreeCAD's central workspace (matching the Spreadsheet view window style) with clean canvas.
- **Real-Time Node Search**: Filter nodes dynamically by typing in the search bar at the top of the Node Library panel in Tasks view.
- **Automatic Workbench Function Discovery**: Automatically scans FreeCAD workbenches (``Part``, ``Draft``, ``Arch``, ``Mesh``, ``Sketcher``, ``PartDesign``) and dynamically generates scriptable function nodes in the Node Library.
- **Node Context Menu**: Secondary click (right-click) on any node to perform **Cut**, **Copy**, **Paste**, **Duplicate**, or **Detach Links**.
- **Color-Coded Sockets & Labels**: Visual nodes display clear text labels for input/output sockets and distinct data-type color coding (Float, Vector, Shape, String, Boolean, etc.).
- **Visual Programming**: Connect CAD inputs, primitives, features, and boolean operations with a drag-and-drop node graph interface.
- **Parametric CAD Integration**: Instantly generate and update 3D Part features directly in the active FreeCAD document.
- **Extensible Architecture**: Easily create custom node types using standard Python classes.
- **Serialization**: Save and load node graphs to and from JSON files.
- **Cross-Platform Compatibility**: Supports PySide6, PySide2, and PyQt5.

Quick Start
-----------

How to Load in FreeCAD
~~~~~~~~~~~~~~~~~~~~~~

To install and load the NodeGraph Workbench in FreeCAD:

1. Locate your FreeCAD user directory or Mod directory:
   - **Linux**: ``~/.local/share/FreeCAD/Mod/`` or ``~/.FreeCAD/Mod/``
   - **Windows**: ``%APPDATA%\FreeCAD\Mod\``
   - **macOS**: ``~/Library/Application Support/FreeCAD/Mod/``

2. Clone or copy this repository into the ``Mod`` directory:

   .. code-block:: bash

      cd ~/.local/share/FreeCAD/Mod/
      git clone https://github.com/freecad/freecad-nodegraph.git NodeGraph

3. Restart FreeCAD. Select **NodeGraph** from the workbench selector dropdown menu.

How to Use
~~~~~~~~~~

1. Open or create a FreeCAD document.
2. Select a parent object in the Model view if you want to nest the NodeGraph object as a child, or leave unselected for top-level creation.
3. Click **Create NodeGraph Object** in the NodeGraph workbench toolbar or menu to create a NodeGraph object in the Model view tree without forcing focus onto the Tasks view.
4. Selecting any NodeGraph object in the Model view automatically opens and displays its specific node graph canvas tab (titled ``NodeGraph:X``).
5. Use the **Tasks** view panel to search and double-click nodes into the canvas.
6. Connect sockets and modify node parameters in the **Properties Inspector**.
7. Modifications made on the canvas automatically persist directly to the document object's ``GraphData`` property.
8. Recomputing the FreeCAD document automatically evaluates the NodeGraph object and updates its 3D Shape.

Documentation
-------------

Full documentation is hosted on Read the Docs:
`https://freecad-nodegraph.readthedocs.io/ <https://freecad-nodegraph.readthedocs.io/>`_

License
-------

Distributed under the LGPL v2.1 License.
