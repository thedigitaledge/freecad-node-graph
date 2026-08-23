Usage Guide
===========

Opening the Editor
------------------

1. Switch to the **NodeGraph** workbench in FreeCAD.
2. Click **Open Node Graph Editor** in the toolbar or menu.
3. A window will appear containing the Node Library, Workbench Toolbars, Node Canvas, and Properties Inspector.

Building a Node Graph
---------------------

Workbench Toolbars & Action Buttons
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The editor header automatically displays toolbars for each discovered FreeCAD workbench (e.g. ``[Part]``, ``[Draft]``, ``[Arch]``, ``[Mesh]``). Each toolbar contains action buttons corresponding to scriptable functions (e.g. *Box*, *Cylinder*, *Sphere*, *Wall*, *Polygon*). Click any button to instantly spawn that node onto the canvas.

Node Library Palette
~~~~~~~~~~~~~~~~~~~~
In the **Node Library** panel on the left side, double-click any node category to expand it, then double-click a node type to place it on the canvas.

Connecting Sockets
~~~~~~~~~~~~~~~~~~
Click and drag from an output socket (right side of a node) to an input socket (left side of another node). A connecting line will appear.

Inspecting Properties
~~~~~~~~~~~~~~~~~~~~~
Click on a node to view and edit its parameters in the **Properties Inspector** on the right panel.

Executing the Graph
-------------------

Click the **Run Graph** button on the editor toolbar or run the command from FreeCAD. The graph evaluator will topologically sort the DAG and compute all nodes, updating or creating 3D Part objects in the active FreeCAD document.

Saving & Loading Graphs
-----------------------

Use **Save Graph...** and **Load Graph...** in the toolbar to save your node setup as a JSON file.
