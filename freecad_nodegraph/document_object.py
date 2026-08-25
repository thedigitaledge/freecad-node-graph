"""DocumentObject FeaturePython implementation for NodeGraph objects in FreeCAD Model tree."""

import json

try:
    import FreeCAD
    import FreeCADGui
    HAS_FREECAD = True
except ImportError:
    HAS_FREECAD = False


class NodeGraphObject:
    """FeaturePython object storing graph data inside FreeCAD's document model tree."""

    def __init__(self, obj):
        self.Type = "NodeGraph::NodeGraphObject"
        obj.Proxy = self
        self.init_object(obj)

    def init_object(self, obj):
        if not hasattr(obj, "GraphData"):
            obj.addProperty("App::PropertyString", "GraphData", "NodeGraph", "JSON serialized graph data")
            obj.GraphData = "{}"

    def execute(self, obj):
        """Execute/recompute parametric NodeGraph object."""
        pass

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class ViewProviderNodeGraphObject:
    """GUI ViewProvider for NodeGraphObject in FreeCAD tree view."""

    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        return ":/icons/NodeGraph.svg"

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


_mock_count = 0


class MockDocumentObject:
    """Fallback mock object for testing without FreeCAD."""

    def __init__(self, name=None, label=None):
        global _mock_count
        _mock_count += 1
        self.Name = name or f"NodeGraph_{_mock_count}"
        self.Label = label or f"NodeGraph:{_mock_count}"
        self.GraphData = "{}"
        self.Group = []
        self.Proxy = NodeGraphObject(self)

    def addObject(self, child):
        self.Group.append(child)


def get_nodegraph_count(doc=None) -> int:
    """Calculate total count of NodeGraph objects in active document."""
    if HAS_FREECAD and doc:
        count = 0
        for obj in doc.Objects:
            if hasattr(obj, "Proxy") and isinstance(obj.Proxy, NodeGraphObject):
                count += 1
            elif "NodeGraph" in getattr(obj, "Name", ""):
                count += 1
        return count + 1
    return 1


def create_nodegraph_object(doc=None, parent_obj=None):
    """Create a new NodeGraph document object supporting top-level or sub-branch nesting."""
    if HAS_FREECAD:
        if doc is None:
            doc = FreeCAD.ActiveDocument
            if doc is None:
                doc = FreeCAD.newDocument("NodeGraphDoc")

        count = get_nodegraph_count(doc)
        obj_name = f"NodeGraph_{count}"
        label_name = f"NodeGraph:{count}"

        obj = doc.addObject("App::FeaturePython", obj_name)
        NodeGraphObject(obj)
        if hasattr(obj, "Label"):
            obj.Label = label_name

        if HAS_FREECAD and hasattr(FreeCADGui, "loaded") and FreeCADGui.loaded():
            ViewProviderNodeGraphObject(obj.ViewObject)

        # Nest under parent object (sub-branch) if provided, otherwise top-level
        if parent_obj:
            if hasattr(parent_obj, "addObject"):
                parent_obj.addObject(obj)
            elif hasattr(parent_obj, "Group"):
                group_list = list(getattr(parent_obj, "Group", []))
                if obj not in group_list:
                    group_list.append(obj)
                    parent_obj.Group = group_list

        doc.recompute()
        return obj
    else:
        # Fallback for standalone/testing
        obj = MockDocumentObject()
        if parent_obj:
            if hasattr(parent_obj, "addObject"):
                parent_obj.addObject(obj)
            elif hasattr(parent_obj, "Group"):
                parent_obj.Group.append(obj)
        return obj


class NodeGraphSelectionObserver:
    """Selection observer to open and focus NodeGraph editor workspace view when object is selected in tree."""

    def __init__(self):
        self._active = True

    def addSelection(self, doc_name, obj_name, sub_name, pos):
        if not HAS_FREECAD or not self._active:
            return
        try:
            doc = FreeCAD.getDocument(doc_name) if hasattr(FreeCAD, "getDocument") else None
            if not doc:
                return
            obj = doc.getObject(obj_name)
            if obj and hasattr(obj, "Proxy") and isinstance(obj.Proxy, NodeGraphObject):
                from freecad_nodegraph.commands import open_editor_for_nodegraph_object
                open_editor_for_nodegraph_object(obj)
        except Exception as e:
            if hasattr(FreeCAD, "Console"):
                FreeCAD.Console.PrintError(f"NodeGraph Selection Observer Error: {e}\n")


def register_selection_observer():
    if HAS_FREECAD and hasattr(FreeCADGui, "Selection"):
        observer = NodeGraphSelectionObserver()
        FreeCADGui.Selection.addObserver(observer)
        return observer
    return None
