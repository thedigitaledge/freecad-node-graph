========================================================
Blender Node Graph Architecture & FreeCAD Implementation
========================================================

This document provides a detailed technical analysis of Blender's node graph system architecture, focusing on high-level design, evaluation/action execution mechanics, and data persistence models, followed by a comparison with the **FreeCAD NodeGraph Workbench** implementation.

1. High-Level View of Blender's Node Graph System
=================================================

Blender utilizes node graph visual programming across multiple subsystems:

- **Shader Nodes** (Materials, World, Light)
- **Geometry Nodes** (Procedural modeling and visual scripting)
- **Compositor Nodes** (Post-processing and image manipulation)
- **Texture Nodes** (Legacy texture generation)

Core Data Abstractions
----------------------

At the core of Blender's C/C++ DNA/RNA architecture (and reflected in `bpy.types`), node systems consist of four core entities:

1. **Node Tree (`bNodeTree` / `bpy.types.NodeTree`)**:
   The top-level container data block (`ID` data block). It owns collections of nodes, links, inputs, and outputs. Node trees can be shared across multiple materials, modifiers, or groups.

2. **Node (`bNode` / `bpy.types.Node`)**:
   Individual processing units placed on the canvas. A node defines inputs (`inputs`), outputs (`outputs`), internal UI parameters/properties, and internal processing logic.

3. **Socket (`bNodeSocket` / `bpy.types.NodeSocket`)**:
   Typed ports on nodes. Common data types include `Float`, `Vector`, `RGBA Color`, `Geometry`, `Object`, `Collection`, `Boolean`, `String`, `Shader`, and `Matrix`. Sockets store fallback values (`default_value`) used when no incoming link is connected.

4. **Link (`bNodeLink` / `bpy.types.NodeLink`)**:
   A directed connection pointing from an output socket (`from_node`, `from_socket`) to an input socket (`to_node`, `to_socket`).

5. **Node Groups**:
   Node trees can be embedded inside other node trees via Group Nodes (`NodeTreeInputs` / `NodeTreeOutputs`), enabling hierarchical abstraction and reusability.


2. Detailed View: How Nodes are Converted to Actions (Execution Model)
======================================================================

Blender converts visual node graphs into concrete actions and geometry transformations using a **Directed Acyclic Graph (DAG) Execution Pipeline**.

Topological Dependency Graph & Culling
--------------------------------------

1. **Backward Traversal from Terminal Output Nodes**:
   When evaluation is triggered (e.g., scene recompute or frame change), evaluation begins at terminal output nodes (such as `Group Output` or `Material Output`).
2. **Dead-Code Elimination**:
   Nodes that are not reachable via incoming connections to active output nodes are excluded from the execution schedule.
3. **Topological Sort**:
   Reachable nodes are sorted into a valid execution order where every node is scheduled *after* all nodes supplying its inputs.

Execution Pipeline Mechanics (Geometry Nodes & Fields)
------------------------------------------------------

Modern Blender Geometry Nodes (version 3.0+) uses a **Fields & Lazy Evaluation Engine** written in C++:

- **Field System**:
  Instead of evaluating heavy geometry data eagerly at every node, sockets can pass *Fields*—lazy functions that describe data operations (e.g., "position + offset").
- **Node C++ Execution Context (`GeoNodeExecParams`)**:
  Each C++ node implementation inherits from base node classes (e.g., `nodes::NodeSimple`). During evaluation, the evaluator provides `GeoNodeExecParams`:

  - `params.get_input<T>("SocketName")`: Evaluates upstream inputs or returns default socket values.
  - `params.set_output("SocketName", result)`: Sets computed output data or field functions onto output sockets.
- **Action Dispatch**:
  Geometry operations invoke C++ BMesh, C++ Mesh primitive generators, or OpenVDB libraries, producing mutated `GeometrySet` structures passed down the pipeline.


3. Detailed View: How Data is Stored
====================================

Persistence in `.blend` Files (DNA & RNA Architecture)
------------------------------------------------------

Blender stores all data using a C struct serialization format known as **DNA** (`DNA_node_types.h`):

1. **Binary Storage**:
   - `bNodeTree` structs are serialized directly into `.blend` binary blocks.
   - Sockets and links are stored as C double-linked lists (`ListBase nodes`, `ListBase links`).
2. **Node Data Layout (`bNode`)**:
   - `typeinfo`: References the node definition structure (`bNodeType`).
   - `locx`, `locy`: Canvas coordinates for UI rendering.
   - `width`, `height`: Visual dimension bounds.
   - `storage`: Void pointer or specific struct holding custom node parameters (e.g., `NodeGeometryCurvePrimitiveCircle`).
   - `custom1`, `custom2`: Bitflags and enum indices.
3. **RNA Dynamic Properties**:
   Blender exposes C DNA structures to Python via the **RNA** reflection API (`bpy.types.Node.bl_idname`, `bpy.props`). Sockets dynamically adapt properties based on custom node registration.


4. Comparison: FreeCAD Python NodeGraph Architecture
====================================================

The **FreeCAD NodeGraph Workbench** (`freecad_nodegraph`) adopts a similar architecture tailored to FreeCAD's parametric C++ / Python core:

+---------------------+---------------------------------+-----------------------------------+
| Component           | Blender Implementation          | FreeCAD Implementation            |
+=====================+=================================+===================================+
| **Graph Container** | `bNodeTree`                     | `freecad_nodegraph.core.NodeGraph`|
+---------------------+---------------------------------+-----------------------------------+
| **Base Node**       | `bNode` / `bpy.types.Node`      | `freecad_nodegraph.core.BaseNode` |
+---------------------+---------------------------------+-----------------------------------+
| **Evaluation**      | C++ `GeoNodeExec` / Field Engine| `core.evaluator.GraphEvaluator`   |
+---------------------+---------------------------------+-----------------------------------+
| **Actions**         | C++ BMesh / `GeometrySet`       | FreeCAD Part API (`Part.makeBox`) |
+---------------------+---------------------------------+-----------------------------------+
| **Persistence**     | `.blend` binary DNA structs     | FeaturePython `GraphData` JSON    |
+---------------------+---------------------------------+-----------------------------------+

Action Execution in `freecad_nodegraph`
---------------------------------------

1. `GraphEvaluator` computes a topological ordering of `BaseNode` instances in `NodeGraph`.
2. Inputs are resolved from connected output sockets or fallback socket default values.
3. Each node's `evaluate()` method executes Python / FreeCAD Part commands (e.g. `Part.makeBox()`, `shape.fuse()`, `shape.cut()`).
4. `DocumentOutputNode` updates the `Shape` or properties of target document objects in `FreeCAD.ActiveDocument`.

Data Persistence in `freecad_nodegraph`
---------------------------------------

- Node graph instances are encapsulated inside a custom FeaturePython object (`NodeGraphObject`).
- The entire graph layout, node properties, socket defaults, and edge topology are serialized into a single JSON payload stored in the object's `GraphData` property.
- FreeCAD's native document save (`.FCStd`) and Undo/Redo transaction system (`doc.openTransaction` / `doc.commitTransaction`) handle data storage and history tracking seamlessly.
