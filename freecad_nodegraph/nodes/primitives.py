"""3D Primitive Shape nodes for FreeCAD NodeGraph."""

from freecad_nodegraph.core.node import BaseNode
from freecad_nodegraph.core.socket import DataType
from freecad_nodegraph.core.registry import register_node
from freecad_nodegraph.nodes.inputs import create_vector, create_placement, HAS_FREECAD

try:
    import Part
except ImportError:
    Part = None


class MockShape:
    """Mock Part shape representation for testing outside FreeCAD."""
    def __init__(self, shape_type: str, params: dict):
        self.shape_type = shape_type
        self.params = params
        self.Placement = params.get("Placement", create_placement())

    def __repr__(self):
        return f"<MockShape {self.shape_type} {self.params}>"


@register_node
class BoxNode(BaseNode):
    node_type = "BoxNode"
    category = "Geometry"
    title = "Box"

    def setup_sockets(self) -> None:
        self.add_input("Length", DataType.FLOAT, 10.0)
        self.add_input("Width", DataType.FLOAT, 10.0)
        self.add_input("Height", DataType.FLOAT, 10.0)
        self.add_input("Placement", DataType.PLACEMENT, None)
        self.add_output("Shape", DataType.SHAPE)

    def compute(self) -> None:
        length = float(self.get_input_value("Length") or 10.0)
        width = float(self.get_input_value("Width") or 10.0)
        height = float(self.get_input_value("Height") or 10.0)
        placement = self.get_input_value("Placement")

        if Part and HAS_FREECAD:
            shape = Part.makeBox(length, width, height)
            if placement:
                shape.Placement = placement
        else:
            shape = MockShape("Box", {"Length": length, "Width": width, "Height": height, "Placement": placement})

        self.set_output_value("Shape", shape)


@register_node
class CylinderNode(BaseNode):
    node_type = "CylinderNode"
    category = "Geometry"
    title = "Cylinder"

    def setup_sockets(self) -> None:
        self.add_input("Radius", DataType.FLOAT, 5.0)
        self.add_input("Height", DataType.FLOAT, 10.0)
        self.add_input("Placement", DataType.PLACEMENT, None)
        self.add_output("Shape", DataType.SHAPE)

    def compute(self) -> None:
        radius = float(self.get_input_value("Radius") or 5.0)
        height = float(self.get_input_value("Height") or 10.0)
        placement = self.get_input_value("Placement")

        if Part and HAS_FREECAD:
            shape = Part.makeCylinder(radius, height)
            if placement:
                shape.Placement = placement
        else:
            shape = MockShape("Cylinder", {"Radius": radius, "Height": height, "Placement": placement})

        self.set_output_value("Shape", shape)


@register_node
class SphereNode(BaseNode):
    node_type = "SphereNode"
    category = "Geometry"
    title = "Sphere"

    def setup_sockets(self) -> None:
        self.add_input("Radius", DataType.FLOAT, 5.0)
        self.add_input("Placement", DataType.PLACEMENT, None)
        self.add_output("Shape", DataType.SHAPE)

    def compute(self) -> None:
        radius = float(self.get_input_value("Radius") or 5.0)
        placement = self.get_input_value("Placement")

        if Part and HAS_FREECAD:
            shape = Part.makeSphere(radius)
            if placement:
                shape.Placement = placement
        else:
            shape = MockShape("Sphere", {"Radius": radius, "Placement": placement})

        self.set_output_value("Shape", shape)


@register_node
class ConeNode(BaseNode):
    node_type = "ConeNode"
    category = "Geometry"
    title = "Cone"

    def setup_sockets(self) -> None:
        self.add_input("Radius1", DataType.FLOAT, 5.0)
        self.add_input("Radius2", DataType.FLOAT, 0.0)
        self.add_input("Height", DataType.FLOAT, 10.0)
        self.add_input("Placement", DataType.PLACEMENT, None)
        self.add_output("Shape", DataType.SHAPE)

    def compute(self) -> None:
        r1 = float(self.get_input_value("Radius1") or 5.0)
        r2 = float(self.get_input_value("Radius2") or 0.0)
        height = float(self.get_input_value("Height") or 10.0)
        placement = self.get_input_value("Placement")

        if Part and HAS_FREECAD:
            shape = Part.makeCone(r1, r2, height)
            if placement:
                shape.Placement = placement
        else:
            shape = MockShape("Cone", {"Radius1": r1, "Radius2": r2, "Height": height, "Placement": placement})

        self.set_output_value("Shape", shape)
