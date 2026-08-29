"""Serializer module for JSON save/load operations on graphs."""

import json
from typing import Dict, Any, Optional
from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.node import BaseNode
from freecad_nodegraph.core.edge import Edge
from freecad_nodegraph.core.registry import NodeRegistry


class GraphSerializer:
    """Handles serialization and deserialization of Node Graphs to/from dicts and JSON files."""

    @staticmethod
    def to_dict(graph: Graph) -> Dict[str, Any]:
        """Serialize a Graph instance to a dictionary."""
        nodes_data = []
        for node in graph.nodes:
            inputs_data = {}
            for sock in node.inputs:
                inputs_data[sock.name] = sock.default_value

            node_info = {
                "id": node.id,
                "node_type": getattr(node, "node_type", node.__class__.__name__),
                "title": node.title,
                "pos_x": getattr(node, "pos_x", 0.0),
                "pos_y": getattr(node, "pos_y", 0.0),
                "inputs": inputs_data,
            }
            # Add custom serialization method if implemented by node
            if hasattr(node, "custom_serialize"):
                node_info["custom_data"] = node.custom_serialize()

            nodes_data.append(node_info)

        edges_data = []
        for edge in graph.edges:
            if edge.start_socket and edge.end_socket:
                edges_data.append(
                    {
                        "id": edge.id,
                        "start_node_id": edge.start_socket.node.id,
                        "start_socket_name": edge.start_socket.name,
                        "end_node_id": edge.end_socket.node.id,
                        "end_socket_name": edge.end_socket.name,
                    }
                )

        return {
            "version": "1.0",
            "nodes": nodes_data,
            "edges": edges_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], graph: Optional[Graph] = None) -> Graph:
        """Deserialize a dictionary to populate or create a Graph."""
        if graph is None:
            graph = Graph()
        else:
            graph.clear()

        node_map: Dict[str, BaseNode] = {}

        for node_data in data.get("nodes", []):
            node_type = node_data.get("node_type")
            node_cls = NodeRegistry.get_node_class(node_type)
            if not node_cls:
                continue

            node = node_cls(
                graph=graph,
                node_id=node_data.get("id"),
                title=node_data.get("title"),
            )
            node.pos_x = node_data.get("pos_x", 0.0)
            node.pos_y = node_data.get("pos_y", 0.0)

            # Restore default values for inputs
            inputs_data = node_data.get("inputs", {})
            for sock in node.inputs:
                if sock.name in inputs_data:
                    sock.default_value = inputs_data[sock.name]

            # Restore custom data if applicable
            if hasattr(node, "custom_deserialize") and "custom_data" in node_data:
                node.custom_deserialize(node_data["custom_data"])

            graph.add_node(node)
            node_map[node.id] = node

        for edge_data in data.get("edges", []):
            start_node = node_map.get(edge_data.get("start_node_id"))
            end_node = node_map.get(edge_data.get("end_node_id"))

            if start_node and end_node:
                start_sock = start_node.get_output_socket(
                    edge_data.get("start_socket_name")
                )
                end_sock = end_node.get_input_socket(edge_data.get("end_socket_name"))

                if start_sock and end_sock:
                    graph.connect_sockets(start_sock, end_sock)

        return graph

    @classmethod
    def save_to_file(cls, graph: Graph, filepath: str) -> None:
        """Save graph to JSON file."""
        data = cls.to_dict(graph)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str, graph: Optional[Graph] = None) -> Graph:
        """Load graph from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data, graph=graph)
