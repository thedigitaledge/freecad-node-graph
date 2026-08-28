"""Base Node class for all node graph nodes."""

import uuid
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING
from freecad_nodegraph.core.socket import Socket, SocketType, DataType

if TYPE_CHECKING:
    from freecad_nodegraph.core.graph import Graph


class BaseNode:
    """Abstract base class for nodes in the node-graph."""

    node_type: str = "BaseNode"
    category: str = "General"
    title: str = "Base Node"

    def __init__(
        self,
        graph: Optional["Graph"] = None,
        node_id: Optional[str] = None,
        title: Optional[str] = None,
    ):
        self.id: str = node_id or str(uuid.uuid4())
        self.graph: Optional["Graph"] = graph
        if title:
            self.title = title

        self.pos_x: float = 0.0
        self.pos_y: float = 0.0

        self.inputs: List[Socket] = []
        self.outputs: List[Socket] = []
        self._outputs_cache: Dict[str, Any] = {}
        self.is_dirty: bool = True

        self.setup_sockets()

    @classmethod
    def get_help_summary(cls) -> str:
        """Extract the first non-empty line from the node class docstring."""
        doc = cls.__doc__
        if doc:
            lines = [line.strip() for line in doc.strip().splitlines() if line.strip()]
            if lines:
                return lines[0]
        return getattr(cls, "title", "Node")

    def setup_sockets(self) -> None:
        """Override in subclasses to define input and output sockets."""
        pass

    def add_input(
        self,
        name: str,
        data_type: DataType = DataType.ANY,
        default_value: Any = None,
        socket_id: Optional[str] = None,
    ) -> Socket:
        socket = Socket(
            node=self,
            name=name,
            socket_type=SocketType.INPUT,
            data_type=data_type,
            value=default_value,
            socket_id=socket_id,
        )
        self.inputs.append(socket)
        return socket

    def add_output(
        self,
        name: str,
        data_type: DataType = DataType.ANY,
        socket_id: Optional[str] = None,
    ) -> Socket:
        socket = Socket(
            node=self,
            name=name,
            socket_type=SocketType.OUTPUT,
            data_type=data_type,
            socket_id=socket_id,
        )
        self.outputs.append(socket)
        return socket

    def get_input_socket(self, name: str) -> Optional[Socket]:
        for socket in self.inputs:
            if socket.name == name:
                return socket
        return None

    def get_output_socket(self, name: str) -> Optional[Socket]:
        for socket in self.outputs:
            if socket.name == name:
                return socket
        return None

    def get_input_value(self, name: str) -> Any:
        socket = self.get_input_socket(name)
        if socket:
            return socket.get_value()
        return None

    def get_output_value(self, name: str) -> Any:
        if self.is_dirty:
            self.compute()
            self.is_dirty = False
        return self._outputs_cache.get(name)

    def set_output_value(self, name: str, value: Any) -> None:
        self._outputs_cache[name] = value

    def mark_dirty(self, visited: Optional[Set["BaseNode"]] = None) -> None:
        """Mark this node and downstream nodes as dirty, preventing recursion loops."""
        if visited is None:
            visited = set()
        if self in visited:
            return
        visited.add(self)

        self.is_dirty = True
        for output_socket in self.outputs:
            for edge in output_socket.edges:
                if edge.end_socket and edge.end_socket.node:
                    edge.end_socket.node.mark_dirty(visited)

    def mark_clean(self) -> None:
        self.is_dirty = False

    def compute(self) -> None:
        """Override in subclasses to calculate output values from input values."""
        pass

    def get_upstream_nodes(self) -> List["BaseNode"]:
        """Returns all directly connected upstream nodes."""
        nodes = []
        for socket in self.inputs:
            for edge in socket.edges:
                if edge.start_socket and edge.start_socket.node:
                    upstream_node = edge.start_socket.node
                    if upstream_node not in nodes:
                        nodes.append(upstream_node)
        return nodes

    def get_downstream_nodes(self) -> List["BaseNode"]:
        """Returns all directly connected downstream nodes."""
        nodes = []
        for socket in self.outputs:
            for edge in socket.edges:
                if edge.end_socket and edge.end_socket.node:
                    downstream_node = edge.end_socket.node
                    if downstream_node not in nodes:
                        nodes.append(downstream_node)
        return nodes

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "node_type": self.node_type,
            "title": self.title,
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "inputs": [sock.to_dict() for sock in self.inputs],
            "outputs": [sock.to_dict() for sock in self.outputs],
        }
