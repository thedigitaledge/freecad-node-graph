"""Input and Value nodes for node graph."""

from freecad_nodegraph.core.node import BaseNode
from freecad_nodegraph.core.socket import DataType
from freecad_nodegraph.core.registry import register_node

try:
    import FreeCAD
    HAS_FREECAD = True
except ImportError:
    HAS_FREECAD = False


class MockVector:
    """Fallback Vector class when FreeCAD is not available."""
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self):
        return f"Vector ({self.x}, {self.y}, {self.z})"

    def __eq__(self, other):
        if hasattr(other, 'x') and hasattr(other, 'y') and hasattr(other, 'z'):
            return (self.x, self.y, self.z) == (other.x, other.y, other.z)
        return False


class MockPlacement:
    """Fallback Placement class when FreeCAD is not available."""
    def __init__(self, Base=None, Rotation=None):
        self.Base = Base or MockVector(0, 0, 0)
        self.Rotation = Rotation or (0, 0, 0, 1)

    def __repr__(self):
        return f"Placement [Base: {self.Base}]"


def create_vector(x: float, y: float, z: float):
    if HAS_FREECAD:
        return FreeCAD.Vector(x, y, z)
    return MockVector(x, y, z)


def create_placement(pos=None):
    if HAS_FREECAD:
        p = FreeCAD.Placement()
        if pos:
            p.Base = pos
        return p
    return MockPlacement(Base=pos)


@register_node
class FloatNode(BaseNode):
    node_type = "FloatNode"
    category = "Input"
    title = "Float Value"

    def setup_sockets(self) -> None:
        self.add_input("Value", DataType.FLOAT, 0.0)
        self.add_output("Value", DataType.FLOAT)

    def compute(self) -> None:
        val = self.get_input_value("Value")
        self.set_output_value("Value", float(val) if val is not None else 0.0)


@register_node
class IntegerNode(BaseNode):
    node_type = "IntegerNode"
    category = "Input"
    title = "Integer Value"

    def setup_sockets(self) -> None:
        self.add_input("Value", DataType.INTEGER, 0)
        self.add_output("Value", DataType.INTEGER)

    def compute(self) -> None:
        val = self.get_input_value("Value")
        self.set_output_value("Value", int(val) if val is not None else 0)


@register_node
class StringNode(BaseNode):
    node_type = "StringNode"
    category = "Input"
    title = "String Value"

    def setup_sockets(self) -> None:
        self.add_input("Value", DataType.STRING, "")
        self.add_output("Value", DataType.STRING)

    def compute(self) -> None:
        val = self.get_input_value("Value")
        self.set_output_value("Value", str(val) if val is not None else "")


@register_node
class BooleanNode(BaseNode):
    node_type = "BooleanNode"
    category = "Input"
    title = "Boolean Value"

    def setup_sockets(self) -> None:
        self.add_input("Value", DataType.BOOLEAN, False)
        self.add_output("Value", DataType.BOOLEAN)

    def compute(self) -> None:
        val = self.get_input_value("Value")
        self.set_output_value("Value", bool(val) if val is not None else False)


@register_node
class VectorNode(BaseNode):
    node_type = "VectorNode"
    category = "Input"
    title = "Vector"

    def setup_sockets(self) -> None:
        self.add_input("X", DataType.FLOAT, 0.0)
        self.add_input("Y", DataType.FLOAT, 0.0)
        self.add_input("Z", DataType.FLOAT, 0.0)
        self.add_output("Vector", DataType.VECTOR)

    def compute(self) -> None:
        x = float(self.get_input_value("X") or 0.0)
        y = float(self.get_input_value("Y") or 0.0)
        z = float(self.get_input_value("Z") or 0.0)
        vec = create_vector(x, y, z)
        self.set_output_value("Vector", vec)


@register_node
class PlacementNode(BaseNode):
    node_type = "PlacementNode"
    category = "Input"
    title = "Placement"

    def setup_sockets(self) -> None:
        self.add_input("Position", DataType.VECTOR, None)
        self.add_output("Placement", DataType.PLACEMENT)

    def compute(self) -> None:
        pos = self.get_input_value("Position")
        if pos is None:
            pos = create_vector(0.0, 0.0, 0.0)
        placement = create_placement(pos)
        self.set_output_value("Placement", placement)
