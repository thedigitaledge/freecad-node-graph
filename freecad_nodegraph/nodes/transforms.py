"""Transformation and Feature nodes for FreeCAD NodeGraph."""

from freecad_nodegraph.core.node import BaseNode
from freecad_nodegraph.core.socket import DataType
from freecad_nodegraph.core.registry import register_node
from freecad_nodegraph.nodes.inputs import create_vector, HAS_FREECAD
from freecad_nodegraph.nodes.primitives import MockShape, Part


@register_node
class TranslateNode(BaseNode):
    node_type = "TranslateNode"
    category = "Transforms"
    title = "Translate"

    def setup_sockets(self) -> None:
        self.add_input("Shape", DataType.SHAPE, None)
        self.add_input("Vector", DataType.VECTOR, None)
        self.add_output("Shape", DataType.SHAPE)

    def compute(self) -> None:
        shape = self.get_input_value("Shape")
        vec = self.get_input_value("Vector") or create_vector(0.0, 0.0, 0.0)

        if shape is None:
            res = None
        else:
            if Part and HAS_FREECAD and hasattr(shape, "copy"):
                res = shape.copy()
                res.translate(vec)
            else:
                res = MockShape("Translate", {"shape": shape, "vector": vec})

        self.set_output_value("Shape", res)


@register_node
class ExtrudeNode(BaseNode):
    node_type = "ExtrudeNode"
    category = "Features"
    title = "Extrude"

    def setup_sockets(self) -> None:
        self.add_input("Shape", DataType.SHAPE, None)
        self.add_input("Vector", DataType.VECTOR, None)
        self.add_output("Shape", DataType.SHAPE)

    def compute(self) -> None:
        shape = self.get_input_value("Shape")
        vec = self.get_input_value("Vector") or create_vector(0.0, 0.0, 10.0)

        if shape is None:
            res = None
        else:
            if Part and HAS_FREECAD and hasattr(shape, "extrude"):
                res = shape.extrude(vec)
            else:
                res = MockShape("Extrude", {"shape": shape, "vector": vec})

        self.set_output_value("Shape", res)


@register_node
class CompoundNode(BaseNode):
    node_type = "CompoundNode"
    category = "Features"
    title = "Compound"

    def setup_sockets(self) -> None:
        self.add_input("Shape 1", DataType.SHAPE, None)
        self.add_input("Shape 2", DataType.SHAPE, None)
        self.add_output("Shape", DataType.SHAPE)

    def compute(self) -> None:
        s1 = self.get_input_value("Shape 1")
        s2 = self.get_input_value("Shape 2")

        shapes = [s for s in [s1, s2] if s is not None]

        if not shapes:
            res = None
        elif len(shapes) == 1:
            res = shapes[0]
        else:
            if Part and HAS_FREECAD and hasattr(Part, "makeCompound"):
                res = Part.makeCompound(shapes)
            else:
                res = MockShape("Compound", {"shapes": shapes})

        self.set_output_value("Shape", res)
