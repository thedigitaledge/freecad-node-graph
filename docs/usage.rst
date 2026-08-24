Usage Guide
===========

Creating NodeGraph Objects & Data Storage in FreeCAD Model View
---------------------------------------------------------------

1. Switch to the **NodeGraph** workbench in FreeCAD.
2. Select a parent group/body/subobject in the Model tree view (or leave nothing selected for top-level creation).
3. Click **Create NodeGraph Object** on the toolbar or menu.
4. A new ``NodeGraph`` FeaturePython object is created in the Model view with its own isolated graph data storage saved in its ``GraphData`` property.
5. Selecting any ``NodeGraph`` object in the Model view automatically opens its editor canvas tab and the Tasks view Node Library panel containing only that object's graph data.

Opening the Editor & Tasks View
-------------------------------

1. Selecting a NodeGraph object in the Model view, clicking **Open Node Graph** in the toolbar, or double-clicking a NodeGraph object opens the editor bound to that object.
2. The Node Graph canvas view opens as a tab in FreeCAD's main document workspace (matching the Spreadsheet view style).
3. The **Node Library** palette and Properties Inspector appear inside FreeCAD's **Tasks** view panel.

Building a Node Graph
---------------------

Tasks View Node Library & Search
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Use the **Search** input box at the top of the **Tasks** view panel to dynamically filter nodes by name in real-time. Double-click any node to add it to the canvas.

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

Connecting Sockets & Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Drag connections between output sockets and input sockets. Select a node to modify its input default values in the **Properties Inspector**.

Document Storage Persistence & Recomputation
--------------------------------------------

All node additions, removals, and connections made in the editor automatically persist into the active FreeCAD document object's ``GraphData`` property. Recomputing the FreeCAD document (or clicking **Run Graph**) evaluates the node graph and assigns the computed 3D geometry to the NodeGraph object's ``Shape`` property.
