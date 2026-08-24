Usage Guide
===========

Opening the Editor
------------------

1. Switch to the **NodeGraph** workbench in FreeCAD.
2. Click **Open Node Graph** in the toolbar or menu.
3. The Node Graph canvas view opens as a tab in FreeCAD's main document workspace (matching the Spreadsheet view style).
4. The **Node Library** palette and Properties Inspector appear as a new tab inside FreeCAD's ComboView / Task dock panel (alongside "Model" and "Tasks").
5. Selecting or focusing the NodeGraph editor workspace tab automatically focuses and shows the **Node Library** tab.

Building a Node Graph
---------------------

Real-Time Node Search
~~~~~~~~~~~~~~~~~~~~~
At the top of the **Node Library** tab, type keywords in the **Search** input box to dynamically filter nodes by name in real-time.

Node Library Palette
~~~~~~~~~~~~~~~~~~~~
In the Node Library tree, double-click any category to expand it, then double-click a node type to add it to the graph canvas.

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
Click on a node to view and edit its parameters in the **Properties Inspector** section of the side panel.

Executing the Graph
-------------------

Click the **Run Graph** button on the FreeCAD toolbar. The graph evaluator will topologically sort the DAG and compute all nodes, updating or creating 3D Part objects in the active FreeCAD document.

Saving & Loading Graphs
-----------------------

Use **Save Graph...** and **Load Graph...** in the FreeCAD toolbar to save your node setup as a JSON file.
