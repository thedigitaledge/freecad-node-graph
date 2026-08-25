Usage Guide
===========

Opening the Editor
------------------

1. Switch to the **NodeGraph** workbench in FreeCAD.
2. Click **Open Node Graph Editor** in the toolbar or menu.
3. A window will appear containing the Node Library, Workbench Toolbars, Node Canvas, Properties Inspector, and AI Assistant.

Building a Node Graph
---------------------

AI Assistant & Prompt-to-Graph
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The editor includes an **AI Assistant** panel (accessible on the right tab panel or via the **AI Assistant** toolbar button).

- Type natural language descriptions (e.g. *"Create a box of 20x20x30 and cut a cylinder of radius 5"*).
- Select preset examples from the dropdown menu.
- Click **Generate Graph** to automatically synthesize nodes, set parameters, and wire connections on the canvas.
- Add an **AI Generator** or **AI Prompt Assistant** node directly from the Node Library under category **AI**.

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
