"""Graph container module managing nodes and edges."""

from typing import Dict, List, Optional, Tuple
from freecad_nodegraph.core.node import BaseNode
from freecad_nodegraph.core.edge import Edge
from freecad_nodegraph.core.socket import Socket


class Graph:
    """Graph structure managing nodes and edges."""

    def __init__(self):
        self.nodes: List[BaseNode] = []
        self.edges: List[Edge] = []
        self.node_map: Dict[str, BaseNode] = {}

    def add_node(self, node: BaseNode) -> BaseNode:
        if node not in self.nodes:
            self.nodes.append(node)
            self.node_map[node.id] = node
            node.graph = self
        return node

    def remove_node(self, node: BaseNode) -> None:
        if node in self.nodes:
            # Remove all edges attached to node sockets
            for socket in node.inputs + node.outputs:
                socket.remove_all_edges()

            self.nodes.remove(node)
            if node.id in self.node_map:
                del self.node_map[node.id]
            node.graph = None

    def add_edge(self, edge: Edge) -> Edge:
        if edge not in self.edges:
            self.edges.append(edge)
            edge.graph = self
            if edge.end_socket and edge.end_socket.node:
                edge.end_socket.node.mark_dirty()
        return edge

    def remove_edge(self, edge: Edge) -> None:
        if edge in self.edges:
            self.edges.remove(edge)
            end_node = edge.end_socket.node if edge.end_socket else None
            edge.remove()
            if end_node:
                end_node.mark_dirty()

    def connect_sockets(
        self, start_socket: Socket, end_socket: Socket
    ) -> Optional[Edge]:
        """Connect an output socket to an input socket."""
        if not start_socket or not end_socket:
            return None

        # Sockets must belong to different nodes
        if start_socket.node == end_socket.node:
            return None

        # Ensure start_socket is output and end_socket is input
        if start_socket.is_input and end_socket.is_output:
            start_socket, end_socket = end_socket, start_socket

        if not (start_socket.is_output and end_socket.is_input):
            return None

        # Remove existing edge connected to input socket (inputs single connection)
        for existing_edge in list(end_socket.edges):
            self.remove_edge(existing_edge)

        edge = Edge(start_socket=start_socket, end_socket=end_socket, graph=self)
        self.add_edge(edge)
        return edge

    def find_node_by_id(self, node_id: str) -> Optional[BaseNode]:
        return self.node_map.get(node_id)

    def find_socket_by_id(self, socket_id: str) -> Optional[Socket]:
        for node in self.nodes:
            for socket in node.inputs + node.outputs:
                if socket.id == socket_id:
                    return socket
        return None

    def clear(self) -> None:
        """Clear all nodes and edges from the graph."""
        for edge in list(self.edges):
            edge.remove()
        self.edges.clear()
        self.nodes.clear()
        self.node_map.clear()

    def to_dict(self) -> dict:
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }
