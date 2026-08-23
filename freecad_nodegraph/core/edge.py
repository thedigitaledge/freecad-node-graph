"""Edge module representing connections between sockets."""

import uuid
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from freecad_nodegraph.core.socket import Socket
    from freecad_nodegraph.core.graph import Graph


class Edge:
    """Connection between an output socket and an input socket."""

    def __init__(
        self,
        start_socket: "Socket",
        end_socket: "Socket",
        graph: Optional["Graph"] = None,
        edge_id: Optional[str] = None,
    ):
        self.id: str = edge_id or str(uuid.uuid4())
        self.start_socket: "Socket" = start_socket
        self.end_socket: "Socket" = end_socket
        self.graph: Optional["Graph"] = graph

        # Register edge with sockets
        if self.start_socket:
            self.start_socket.add_edge(self)
        if self.end_socket:
            self.end_socket.add_edge(self)

    def remove(self) -> None:
        """Disconnect this edge from sockets and remove from graph."""
        if self.start_socket:
            self.start_socket.remove_edge(self)
        if self.end_socket:
            self.end_socket.remove_edge(self)

        if self.graph and self in self.graph.edges:
            self.graph.remove_edge(self)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "start_socket_id": self.start_socket.id if self.start_socket else None,
            "end_socket_id": self.end_socket.id if self.end_socket else None,
        }
