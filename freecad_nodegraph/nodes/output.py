"""Document Output Node for injecting shapes into FreeCAD active document."""

from freecad_nodegraph.core.node import BaseNode
from freecad_nodegraph.core.socket import DataType
from freecad_nodegraph.core.registry import register_node

try:
    import FreeCAD
except ImportError:
    FreeCAD = None


@register_node
class DocumentOutputNode(BaseNode):
    node_type = "DocumentOutputNode"
    category = "Output"
    title = "Document Output"

    def setup_sockets(self) -> None:
        self.add_input("Shape", DataType.SHAPE, None)
        self.add_input("Object Name", DataType.STRING, "NodeGraphResult")

    def compute(self) -> None:
        shape = self.get_input_value("Shape")
        obj_name = str(self.get_input_value("Object Name") or "NodeGraphResult")

        self.last_result_shape = shape
        self.last_object_name = obj_name

        if shape is None:
            return

        if FreeCAD is not None and getattr(FreeCAD, "ActiveDocument", None) is not None:
            doc = FreeCAD.ActiveDocument
            obj = doc.getObject(obj_name)
            if obj is None:
                obj = doc.addObject("Part::Feature", obj_name)

            if hasattr(obj, "Shape"):
                obj.Shape = shape
            doc.recompute()
