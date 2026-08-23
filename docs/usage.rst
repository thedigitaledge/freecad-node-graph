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

Node Context Menu (Secondary Click)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Right-click (secondary click) on any node to open its context menu offering:

- **Cut**: Copy selected node(s) to clipboard and remove from canvas.
- **Copy**: Copy selected node(s) to clipboard.
- **Paste**: Insert copied node(s) onto canvas at an offset position.
- **Duplicate**: Quickly duplicate selected node(s).
- **Detach Links**: Remove all connected edges attached to the node's input and output sockets.

Node Sockets & Color-Coding
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Nodes display text labels next to each input and output socket. Sockets and connection wires are color-coded by value data type:

- **Lime Green**: Float numbers
- **Cyan**: Integers
- **Yellow**: Strings
- **Purple**: Booleans
- **Orange**: 3D Vectors
- **Pink**: Placements
- **Blue**: 3D Part Shapes
- **Teal**: Generic Document Objects
- **Light Gray**: Any / Generic data

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
