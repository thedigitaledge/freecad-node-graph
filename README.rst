FreeCAD NodeGraph Workbench
===========================

.. image:: https://readthedocs.org/projects/freecad-nodegraph/badge/?version=latest
   :target: https://freecad-nodegraph.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

**FreeCAD NodeGraph Workbench** is a visual programming extension for `FreeCAD <https://www.freecad.org/>`_ that enables parametric modeling and CAD feature programming through a node-graph visual scripting interface.

Features
--------

- **AI Assistant & Prompt-to-Graph**: Natural language prompt processor and AI Assistant panel (`AINode` and `AIGraphGenerator`) that converts text descriptions into parametric CAD graphs automatically.
- **Automatic Workbench Function Discovery**: Automatically scans FreeCAD workbenches (``Part``, ``Draft``, ``Arch``, ``Mesh``, ``Sketcher``, ``PartDesign``) and dynamically generates scriptable function nodes and toolbars.
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
2. Click the **Open Node Graph Editor** button on the NodeGraph toolbar.
3. Use the top **Workbench Toolbars** (e.g. ``[Part]``, ``[Draft]``, ``[Arch]``), double-click items in the **Node Library** palette, or open the **AI Assistant** panel to generate node graphs from text prompts.
4. Drag connections between color-coded output sockets and input sockets.
5. Right-click on nodes to **Cut**, **Copy**, **Paste**, **Duplicate**, or **Detach Links**.
6. Select nodes to inspect and modify input parameters in the **Properties Inspector**.
7. Click **Run Graph** to evaluate the DAG and update the FreeCAD document model.

Documentation
-------------

Full documentation is hosted on Read the Docs:
`https://freecad-nodegraph.readthedocs.io/ <https://freecad-nodegraph.readthedocs.io/>`_

License
-------

Distributed under the LGPL v2.1 License.
