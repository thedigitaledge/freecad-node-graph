"""Socket module for node connections."""

import uuid
from enum import Enum, auto
from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from freecad_nodegraph.core.node import BaseNode
    from freecad_nodegraph.core.edge import Edge


class SocketType(Enum):
    INPUT = auto()
    OUTPUT = auto()


class DataType(Enum):
    ANY = "Any"
    FLOAT = "Float"
    INT = "Int"
    STRING = "String"
    BOOLEAN = "Boolean"
    VECTOR = "Vector"
    PLACEMENT = "Placement"
    SHAPE = "Shape"
    OBJECT = "Object"


class Socket:
    """Represents an input or output socket on a node."""

    def __init__(
        self,
        node: "BaseNode",
        name: str,
        socket_type: SocketType,
        data_type: DataType = DataType.ANY,
        value: Any = None,
        socket_id: Optional[str] = None,
    ):
        self.id: str = socket_id or str(uuid.uuid4())
        self.node: "BaseNode" = node
        self.name: str = name
        self.socket_type: SocketType = socket_type
        self.data_type: DataType = data_type
        self.default_value: Any = value
        self.edges: List["Edge"] = []

    @property
    def is_input(self) -> bool:
        return self.socket_type == SocketType.INPUT

    @property
    def is_output(self) -> bool:
        return self.socket_type == SocketType.OUTPUT

    @property
    def is_connected(self) -> bool:
        return len(self.edges) > 0

    def add_edge(self, edge: "Edge") -> None:
        if edge not in self.edges:
            self.edges.append(edge)

    def remove_edge(self, edge: "Edge") -> None:
        if edge in self.edges:
            self.edges.remove(edge)

    def remove_all_edges(self) -> None:
        for edge in list(self.edges):
            edge.remove()

    def get_connected_sockets(self) -> List["Socket"]:
        connected = []
        for edge in self.edges:
            if edge.start_socket == self and edge.end_socket:
                connected.append(edge.end_socket)
            elif edge.end_socket == self and edge.start_socket:
                connected.append(edge.start_socket)
        return connected

    def get_value(self) -> Any:
        """Returns the evaluated value for this socket if input, or cached output."""
        if self.is_input:
            if self.is_connected:
                connected = self.get_connected_sockets()
                if connected:
                    other_socket = connected[0]
                    return other_socket.node.get_output_value(other_socket.name)
            return self.default_value
        else:
            return self.node.get_output_value(self.name)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "socket_type": self.socket_type.name,
            "data_type": self.data_type.value,
            "default_value": self.default_value,
        }
