"""Input and Value nodes for node graph."""

from freecad_nodegraph.core.node import BaseNode
from freecad_nodegraph.core.socket import DataType
from freecad_nodegraph.core.registry import register_node

import FreeCAD


class MockVector:
    """Fallback Vector class when FreeCAD is not available."""

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self):
        return f"Vector ({self.x}, {self.y}, {self.z})"

    def __eq__(self, other):
        if hasattr(other, "x") and hasattr(other, "y") and hasattr(other, "z"):
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
    return FreeCAD.Vector(x, y, z)


def create_placement(pos=None):
    p = FreeCAD.Placement()
    if pos:
        p.Base = pos
    return p


@register_node
class FloatNode(BaseNode):
    node_type = "FloatNode"
    category = "Input"
    title = "Float Value"

    def __init__(self, graph=None, node_id=None, title=None):
        self.value: float = 0.0
        super().__init__(graph=graph, node_id=node_id, title=title)

    def setup_sockets(self) -> None:
        self.add_output("Value", DataType.FLOAT)

    def set_value(self, val) -> None:
        """Set value with error checking for float conversion."""
        try:
            val_float = float(val)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid float value: '{val}'")
        self.value = val_float
        self.mark_dirty()

    def compute(self) -> None:
        self.set_output_value("Value", self.value)

    def custom_serialize(self) -> dict:
        return {"value": self.value}

    def custom_deserialize(self, data: dict) -> None:
        if "value" in data:
            self.set_value(data["value"])


@register_node
class IntegerNode(BaseNode):
    node_type = "IntegerNode"
    category = "Input"
    title = "Integer Value"

    def __init__(self, graph=None, node_id=None, title=None):
        self.value: int = 0
        super().__init__(graph=graph, node_id=node_id, title=title)

    def setup_sockets(self) -> None:
        self.add_output("Value", DataType.INT)

    def set_value(self, val) -> None:
        """Set value with error checking for integer conversion."""
        try:
            val_int = int(val)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid integer value: '{val}'")
        self.value = val_int
        self.mark_dirty()

    def compute(self) -> None:
        self.set_output_value("Value", self.value)

    def custom_serialize(self) -> dict:
        return {"value": self.value}

    def custom_deserialize(self, data: dict) -> None:
        if "value" in data:
            self.set_value(data["value"])


@register_node
class StringNode(BaseNode):
    node_type = "StringNode"
    category = "Input"
    title = "String Value"

    def __init__(self, graph=None, node_id=None, title=None):
        self.value: str = ""
        super().__init__(graph=graph, node_id=node_id, title=title)

    def setup_sockets(self) -> None:
        self.add_output("Value", DataType.STRING)

    def set_value(self, val) -> None:
        """Set value for string data entry."""
        self.value = str(val) if val is not None else ""
        self.mark_dirty()

    def compute(self) -> None:
        self.set_output_value("Value", self.value)

    def custom_serialize(self) -> dict:
        return {"value": self.value}

    def custom_deserialize(self, data: dict) -> None:
        if "value" in data:
            self.set_value(data["value"])


@register_node
class BooleanNode(BaseNode):
    node_type = "BooleanNode"
    category = "Input"
    title = "Boolean Value"

    def __init__(self, graph=None, node_id=None, title=None):
        self.value: bool = False
        super().__init__(graph=graph, node_id=node_id, title=title)

    def setup_sockets(self) -> None:
        self.add_output("Value", DataType.BOOLEAN)

    def set_value(self, val) -> None:
        """Set value with error checking for boolean conversion."""
        if isinstance(val, bool):
            self.value = val
        elif isinstance(val, (int, float)):
            self.value = bool(val)
        elif isinstance(val, str):
            s = val.strip().lower()
            if s in ("true", "1", "yes", "on", "t"):
                self.value = True
            elif s in ("false", "0", "no", "off", "f", ""):
                self.value = False
            else:
                raise ValueError(f"Invalid boolean value: '{val}'")
        else:
            raise ValueError(f"Invalid boolean value: '{val}'")
        self.mark_dirty()

    def compute(self) -> None:
        self.set_output_value("Value", self.value)

    def custom_serialize(self) -> dict:
        return {"value": self.value}

    def custom_deserialize(self, data: dict) -> None:
        if "value" in data:
            self.set_value(data["value"])


@register_node
class VectorNode(BaseNode):
    node_type = "VectorNode"
    category = "Input"
    title = "Vector"

    def __init__(self, graph=None, node_id=None, title=None):
        self.x: float = 0.0
        self.y: float = 0.0
        self.z: float = 0.0
        super().__init__(graph=graph, node_id=node_id, title=title)

    def setup_sockets(self) -> None:
        self.add_output("Vector", DataType.VECTOR)

    def set_components(self, x=None, y=None, z=None) -> None:
        """Set vector components with error checking."""
        if x is not None:
            try:
                self.x = float(x)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid float for X component: '{x}'")
        if y is not None:
            try:
                self.y = float(y)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid float for Y component: '{y}'")
        if z is not None:
            try:
                self.z = float(z)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid float for Z component: '{z}'")
        self.mark_dirty()

    def compute(self) -> None:
        vec = create_vector(self.x, self.y, self.z)
        self.set_output_value("Vector", vec)

    def custom_serialize(self) -> dict:
        return {"x": self.x, "y": self.y, "z": self.z}

    def custom_deserialize(self, data: dict) -> None:
        self.set_components(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            z=data.get("z", 0.0),
        )


@register_node
class PlacementNode(BaseNode):
    node_type = "PlacementNode"
    category = "Input"
    title = "Placement"

    def __init__(self, graph=None, node_id=None, title=None):
        self.pos_x: float = 0.0
        self.pos_y: float = 0.0
        self.pos_z: float = 0.0
        super().__init__(graph=graph, node_id=node_id, title=title)

    def setup_sockets(self) -> None:
        self.add_output("Placement", DataType.PLACEMENT)

    def set_position(self, x=None, y=None, z=None) -> None:
        """Set position vector components with error checking."""
        if x is not None:
            try:
                self.pos_x = float(x)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid float for X position: '{x}'")
        if y is not None:
            try:
                self.pos_y = float(y)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid float for Y position: '{y}'")
        if z is not None:
            try:
                self.pos_z = float(z)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid float for Z position: '{z}'")
        self.mark_dirty()

    def compute(self) -> None:
        pos = create_vector(self.pos_x, self.pos_y, self.pos_z)
        placement = create_placement(pos)
        self.set_output_value("Placement", placement)

    def custom_serialize(self) -> dict:
        return {"pos_x": self.pos_x, "pos_y": self.pos_y, "pos_z": self.pos_z}

    def custom_deserialize(self, data: dict) -> None:
        self.set_position(
            x=data.get("pos_x", 0.0),
            y=data.get("pos_y", 0.0),
            z=data.get("pos_z", 0.0),
        )
