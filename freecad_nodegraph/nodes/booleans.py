"""Boolean operations for FreeCAD NodeGraph."""

from freecad_nodegraph.core.node import BaseNode
from freecad_nodegraph.core.socket import DataType
from freecad_nodegraph.core.registry import register_node
from freecad_nodegraph.nodes.primitives import _get_fallback_shape, Part


@register_node
class FuseNode(BaseNode):
    """Performs a boolean union (fuse) operation between Shape A and Shape B."""

    node_type = "FuseNode"
    category = "Geometry"
    title = "Fuse (Union)"

    def setup_sockets(self) -> None:
        self.add_input("Shape A", DataType.SHAPE, None)
        self.add_input("Shape B", DataType.SHAPE, None)
        self.add_output("Shape", DataType.SHAPE)

    def compute(self) -> None:
        shape_a = self.get_input_value("Shape A")
        shape_b = self.get_input_value("Shape B")

        if shape_a is None:
            res = shape_b
        elif shape_b is None:
            res = shape_a
        else:
            if Part and hasattr(shape_a, "fuse") and hasattr(shape_b, "fuse"):
                res = shape_a.fuse(shape_b)
            else:
                res = _get_fallback_shape("Fuse", {"a": shape_a, "b": shape_b})
        self.set_output_value("Shape", res)


@register_node
class CutNode(BaseNode):
    """Performs a boolean difference (cut) operation subtracting Tool Shape from Base Shape."""

    node_type = "CutNode"
    category = "Geometry"
    title = "Cut (Difference)"

    def setup_sockets(self) -> None:
        self.add_input("Base Shape", DataType.SHAPE, None)
        self.add_input("Tool Shape", DataType.SHAPE, None)
        self.add_output("Shape", DataType.SHAPE)

    def compute(self) -> None:
        base_shape = self.get_input_value("Base Shape")
        tool_shape = self.get_input_value("Tool Shape")

        if base_shape is None:
            res = None
        elif tool_shape is None:
            res = base_shape
        else:
            if Part and hasattr(base_shape, "cut") and hasattr(tool_shape, "cut"):
                res = base_shape.cut(tool_shape)
            else:
                res = _get_fallback_shape("Cut", {"base": base_shape, "tool": tool_shape})

        self.set_output_value("Shape", res)


@register_node
class CommonNode(BaseNode):
    """Performs a boolean intersection (common) operation between Shape A and Shape B."""

    node_type = "CommonNode"
    category = "Geometry"
    title = "Common (Intersection)"

    def setup_sockets(self) -> None:
        self.add_input("Shape A", DataType.SHAPE, None)
        self.add_input("Shape B", DataType.SHAPE, None)
        self.add_output("Shape", DataType.SHAPE)

    def compute(self) -> None:
        shape_a = self.get_input_value("Shape A")
        shape_b = self.get_input_value("Shape B")

        if shape_a is None or shape_b is None:
            res = None
        else:
            if Part and hasattr(shape_a, "common") and hasattr(shape_b, "common"):
                res = shape_a.common(shape_b)
            else:
                res = _get_fallback_shape("Common", {"a": shape_a, "b": shape_b})

        self.set_output_value("Shape", res)
