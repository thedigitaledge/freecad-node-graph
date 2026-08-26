"""FreeCAD FeaturePython Document Object representation for NodeGraph."""

import json
from typing import Optional, Any
from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.evaluator import GraphEvaluator
from freecad_nodegraph.core.serializer import GraphSerializer

try:
    import FreeCAD
except ImportError:
    FreeCAD = None

try:
    import Part
except ImportError:
    Part = None


class NodeGraphObject:
    """FeaturePython proxy class for FreeCAD NodeGraph document objects."""

    def __init__(self, obj: Any):
        obj.Proxy = self
        self.init_properties(obj)

    def init_properties(self, obj: Any) -> None:
        """Initialize custom FreeCAD properties."""
        if not hasattr(obj, "GraphData"):
            obj.addProperty(
                "App::PropertyString",
                "GraphData",
                "NodeGraph",
                "Serialized JSON structure of the node graph",
            )
            # Default empty graph JSON
            empty_graph = Graph()
            obj.GraphData = json.dumps(GraphSerializer.to_dict(empty_graph))

    def onChanged(self, obj: Any, prop: str) -> None:
        """Called by FreeCAD when object property is changed (e.g. via Undo/Redo)."""
        if prop == "GraphData":
            try:
                from freecad_nodegraph.commands import _active_editors
                subwin_info = _active_editors.get(obj)
                if subwin_info:
                    editor = subwin_info[1]
                    if hasattr(editor, "sync_from_document_object"):
                        editor.sync_from_document_object()
            except Exception:
                pass

    def execute(self, obj: Any) -> None:
        """Recompute node graph evaluation and update obj.Shape."""
        if not hasattr(obj, "GraphData") or not obj.GraphData:
            return

        try:
            data = json.loads(obj.GraphData)
            graph = GraphSerializer.from_dict(data)
            evaluator = GraphEvaluator(graph)
            evaluator.evaluate(force=True)

            # Find output shape from graph evaluation
            result_shape = None
            for node in graph.nodes:
                if getattr(node, "node_type", "") == "DocumentOutputNode":
                    result_shape = node.get_input_value("Shape")
                    if result_shape is not None:
                        break

            if result_shape is None:
                # If no output node, find last computed shape from any node
                for node in reversed(graph.nodes):
                    val = node.get_output_value("Shape") or node.get_output_value(
                        "Result"
                    )
                    if val is not None and not isinstance(val, str):
                        result_shape = val
                        break

            if result_shape is not None and hasattr(obj, "Shape"):
                obj.Shape = result_shape

        except Exception as e:
            if FreeCAD and hasattr(FreeCAD, "Console"):
                FreeCAD.Console.PrintError(f"NodeGraphObject recompute error: {e}\n")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class ViewProviderNodeGraph:
    """View provider proxy for NodeGraph document objects in FreeCAD's Model tree view."""

    def __init__(self, vobj: Any):
        vobj.Proxy = self

    def attach(self, vobj: Any):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def getIcon(self):
        return "NodeGraph_Editor"

    def doubleClicked(self, vobj: Any):
        """Open NodeGraph Editor for this object when double-clicked in Model tree view."""
        try:
            from freecad_nodegraph.commands import CommandOpenNodeGraphEditor

            cmd = CommandOpenNodeGraphEditor()
            cmd.Activated(doc_object=getattr(vobj, "Object", None))
            return True
        except Exception:
            return False

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class MockDocumentObject:
    """Mock FreeCAD document object for standalone testing outside FreeCAD."""

    def __init__(self, name: str = "NodeGraph:1"):
        self.Name = name
        self.Label = name
        self.GraphData = ""
        self.Shape = None
        self.Proxy = None
        self.InList = []
        self.OutList = []
        self.Group = []

    def addProperty(
        self, prop_type: str, prop_name: str, group: str = "", doc: str = ""
    ):
        if not hasattr(self, prop_name):
            setattr(self, prop_name, "")

    def addObject(self, child_obj):
        if child_obj not in self.Group:
            self.Group.append(child_obj)
            child_obj.InList.append(self)


def get_next_nodegraph_name(doc: Any = None) -> str:
    """Count existing NodeGraph objects in active document and return 'NodeGraph:X'."""
    count = 1
    if doc is not None:
        for obj in getattr(doc, "Objects", []):
            if (
                getattr(obj, "Proxy", None).__class__.__name__ == "NodeGraphObject"
                or getattr(obj, "Name", "").startswith("NodeGraph")
                or getattr(obj, "Label", "").startswith("NodeGraph")
            ):
                count += 1
    return f"NodeGraph:{count}"


def make_nodegraph_object(
    doc: Any = None,
    name: Optional[str] = None,
    parent_obj: Optional[Any] = None,
) -> Any:
    """Create a NodeGraph document object named 'NodeGraph:X' at top level or nested under subobjects/groups."""
    if name is None:
        name = get_next_nodegraph_name(doc)

    if doc is not None:
        # FreeCAD object name cannot contain colons, so use valid internal name and set Label to 'NodeGraph:X'
        valid_internal_name = name.replace(":", "_")
        obj = doc.addObject("Part::FeaturePython", valid_internal_name)
        obj.Label = name
        NodeGraphObject(obj)
        if hasattr(FreeCAD, "GuiUp") and FreeCAD.GuiUp:
            ViewProviderNodeGraph(obj.ViewObject)

        # Handle nesting inside parent subobject or group
        if parent_obj is not None:
            if hasattr(parent_obj, "addObject"):
                parent_obj.addObject(obj)
            elif hasattr(parent_obj, "Group") and isinstance(parent_obj.Group, list):
                grp = parent_obj.Group
                grp.append(obj)
                parent_obj.Group = grp

        doc.recompute()
        return obj
    else:
        # Fallback mock creation
        obj = MockDocumentObject(name=name)
        NodeGraphObject(obj)
        if parent_obj is not None:
            parent_obj.addObject(obj)
        return obj
