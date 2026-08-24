FreeCAD NodeGraph Workbench
===========================

.. image:: https://readthedocs.org/projects/freecad-nodegraph/badge/?version=latest
   :target: https://freecad-nodegraph.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

**FreeCAD NodeGraph Workbench** is a visual programming extension for `FreeCAD <https://www.freecad.org/>`_ that enables parametric modeling and CAD feature programming through a node-graph visual scripting interface.

Features
--------

- **FreeCAD MDI Main View (Spreadsheet Style)**: Opens the node graph editor directly as a main document tab view in FreeCAD's central workspace (matching the Spreadsheet view window style) with clean canvas and no cluttering toolbars.
- **Node Library Tab in ComboView**: Places the Node Library palette and Properties Inspector into a dedicated tab in FreeCAD's ComboView / Task dock panel (alongside "Model" and "Tasks").
- **Automatic Tab Focus**: Selecting or clicking the NodeGraph editor view automatically switches the active side panel tab to "Node Library".
- **Real-Time Node Search**: Filter nodes dynamically by typing in the search bar at the top of the Node Library panel.
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
2. Click **Open Node Graph** in the NodeGraph workbench toolbar or menu.
3. The NodeGraph canvas view opens as a tab in FreeCAD's main document view area (matching the Spreadsheet view style), while the **Node Library** tab appears in FreeCAD's ComboView / Task panel.
4. Selecting or focusing the NodeGraph view automatically brings the **Node Library** tab into view.
5. Type keywords in the **Search** field at the top of the Node Library tab to quickly filter nodes in real-time.
6. Double-click any node in the palette to add it to the canvas.
7. Drag connections between color-coded output sockets and input sockets.
8. Right-click on nodes to **Cut**, **Copy**, **Paste**, **Duplicate**, or **Detach Links**.
9. Select nodes to inspect and modify input parameters in the **Properties Inspector**.
10. Click **Run Graph** to evaluate the DAG and update the FreeCAD document model.

Documentation
-------------

Full documentation is hosted on Read the Docs:
`https://freecad-nodegraph.readthedocs.io/ <https://freecad-nodegraph.readthedocs.io/>`_

License
-------

Distributed under the LGPL v2.1 License.
