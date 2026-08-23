"""QGraphicsScene for rendering and interacting with the NodeGraph."""

import uuid
try:
    from PySide6.QtWidgets import QGraphicsScene, QGraphicsPathItem
    from PySide6.QtCore import Qt, QPointF
    from PySide6.QtGui import QPen, QColor, QPainter, QBrush
except ImportError:
    try:
        from PySide2.QtWidgets import QGraphicsScene, QGraphicsPathItem
        from PySide2.QtCore import Qt, QPointF
        from PySide2.QtGui import QPen, QColor, QPainter, QBrush
    except ImportError:
        from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPathItem
        from PyQt5.QtCore import Qt, QPointF
        from PyQt5.QtGui import QPen, QColor, QPainter, QBrush

from typing import Dict, List, Optional
from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.node import BaseNode
from freecad_nodegraph.core.socket import Socket
from freecad_nodegraph.core.edge import Edge
from freecad_nodegraph.core.registry import NodeRegistry
from freecad_nodegraph.core.serializer import GraphSerializer
from freecad_nodegraph.gui.items import (
    GraphicsNodeItem,
    GraphicsSocketItem,
    GraphicsEdgeItem,
)


class NodeGraphicsScene(QGraphicsScene):
    """Graphics scene managing node items, edges, clipboard operations, and interactions."""

    def __init__(self, graph: Graph, parent=None):
        super().__init__(parent)
        self.graph = graph

        self.node_items: Dict[BaseNode, GraphicsNodeItem] = {}
        self.edge_items: Dict[Edge, GraphicsEdgeItem] = {}
        self.socket_item_map: Dict[Socket, GraphicsSocketItem] = {}

        self.drag_start_socket: Optional[Socket] = None
        self.drag_edge_item: Optional[QGraphicsPathItem] = None
        self.clipboard_data: Optional[dict] = None

        self.setBackgroundBrush(QBrush(QColor("#222222")))
        self.setSceneRect(-5000, -5000, 10000, 10000)

        self.sync_from_graph()

    def sync_from_graph(self):
        """Rebuild scene graphics items from graph model."""
        self.clear()
        self.node_items.clear()
        self.edge_items.clear()
        self.socket_item_map.clear()

        for node in self.graph.nodes:
            self.add_node_item(node)

        for edge in self.graph.edges:
            self.add_edge_item(edge)

    def add_node_item(self, node: BaseNode) -> GraphicsNodeItem:
        item = GraphicsNodeItem(node)
        self.addItem(item)
        self.node_items[node] = item

        for socket, socket_item in item.socket_items.items():
            self.socket_item_map[socket] = socket_item

        return item

    def remove_node_item(self, node: BaseNode):
        if node in self.node_items:
            item = self.node_items.pop(node)

            for socket in node.inputs + node.outputs:
                if socket in self.socket_item_map:
                    del self.socket_item_map[socket]

            self.removeItem(item)

    def add_edge_item(self, edge: Edge) -> GraphicsEdgeItem:
        item = GraphicsEdgeItem(edge)
        self.addItem(item)
        self.edge_items[edge] = item
        item.update_path()
        return item

    def remove_edge_item(self, edge: Edge):
        if edge in self.edge_items:
            item = self.edge_items.pop(edge)
            self.removeItem(item)

    def get_socket_item(self, socket: Socket) -> Optional[GraphicsSocketItem]:
        return self.socket_item_map.get(socket)

    def update_node_edges(self, node_item: GraphicsNodeItem):
        node = node_item.node
        for socket in node.inputs + node.outputs:
            for edge in socket.edges:
                if edge in self.edge_items:
                    self.edge_items[edge].update_path()

    def detach_node_links(self, node: BaseNode):
        """Remove all edges connected to the specified node's sockets."""
        for socket in node.inputs + node.outputs:
            for edge in list(socket.edges):
                self.remove_edge_item(edge)
                self.graph.remove_edge(edge)

    def copy_selected_nodes(self) -> dict:
        """Copy selected nodes and internal edges to internal clipboard."""
        selected_nodes = [
            item.node for item in self.selectedItems() if isinstance(item, GraphicsNodeItem)
        ]
        if not selected_nodes:
            return {}

        selected_ids = {node.id for node in selected_nodes}
        nodes_data = []

        for node in selected_nodes:
            inputs_data = {sock.name: sock.default_value for sock in node.inputs}
            node_info = {
                "id": node.id,
                "node_type": getattr(node, "node_type", node.__class__.__name__),
                "title": node.title,
                "pos_x": getattr(node, "pos_x", 0.0),
                "pos_y": getattr(node, "pos_y", 0.0),
                "inputs": inputs_data,
            }
            if hasattr(node, "custom_serialize"):
                node_info["custom_data"] = node.custom_serialize()
            nodes_data.append(node_info)

        edges_data = []
        for edge in self.graph.edges:
            if edge.start_socket and edge.end_socket:
                start_nid = edge.start_socket.node.id
                end_nid = edge.end_socket.node.id
                if start_nid in selected_ids and end_nid in selected_ids:
                    edges_data.append({
                        "id": edge.id,
                        "start_node_id": start_nid,
                        "start_socket_name": edge.start_socket.name,
                        "end_node_id": end_nid,
                        "end_socket_name": edge.end_socket.name,
                    })

        self.clipboard_data = {
            "version": "1.0",
            "nodes": nodes_data,
            "edges": edges_data,
        }
        return self.clipboard_data

    def cut_selected_nodes(self) -> dict:
        """Copy selected nodes to clipboard and remove them from graph."""
        data = self.copy_selected_nodes()
        selected_nodes = [
            item.node for item in self.selectedItems() if isinstance(item, GraphicsNodeItem)
        ]
        for node in selected_nodes:
            self.detach_node_links(node)
            self.remove_node_item(node)
            self.graph.remove_node(node)
        return data

    def paste_nodes(self, offset_x: float = 30.0, offset_y: float = 30.0) -> List[BaseNode]:
        """Paste nodes from clipboard data into the graph with remapped unique IDs."""
        if not self.clipboard_data:
            return []

        self.clearSelection()

        id_map: Dict[str, str] = {}
        node_map: Dict[str, BaseNode] = {}
        pasted_nodes: List[BaseNode] = []

        for node_data in self.clipboard_data.get("nodes", []):
            old_id = node_data.get("id")
            new_id = str(uuid.uuid4())
            id_map[old_id] = new_id

            node_type = node_data.get("node_type")
            node_cls = NodeRegistry.get_node_class(node_type)
            if not node_cls:
                continue

            node = node_cls(
                graph=self.graph,
                node_id=new_id,
                title=node_data.get("title"),
            )
            node.pos_x = node_data.get("pos_x", 0.0) + offset_x
            node.pos_y = node_data.get("pos_y", 0.0) + offset_y

            inputs_data = node_data.get("inputs", {})
            for sock in node.inputs:
                if sock.name in inputs_data:
                    sock.default_value = inputs_data[sock.name]

            if hasattr(node, "custom_deserialize") and "custom_data" in node_data:
                node.custom_deserialize(node_data["custom_data"])

            self.graph.add_node(node)
            item = self.add_node_item(node)
            item.setSelected(True)
            pasted_nodes.append(node)
            node_map[new_id] = node

        for edge_data in self.clipboard_data.get("edges", []):
            old_start_id = edge_data.get("start_node_id")
            old_end_id = edge_data.get("end_node_id")

            new_start_id = id_map.get(old_start_id)
            new_end_id = id_map.get(old_end_id)

            if new_start_id and new_end_id:
                start_node = node_map.get(new_start_id)
                end_node = node_map.get(new_end_id)

                if start_node and end_node:
                    start_sock = start_node.get_output_socket(edge_data.get("start_socket_name"))
                    end_sock = end_node.get_input_socket(edge_data.get("end_socket_name"))

                    if start_sock and end_sock:
                        edge = self.graph.connect_sockets(start_sock, end_sock)
                        if edge:
                            self.add_edge_item(edge)

        return pasted_nodes

    def duplicate_selected_nodes(self) -> List[BaseNode]:
        """Copy and paste selected nodes."""
        self.copy_selected_nodes()
        return self.paste_nodes(offset_x=40.0, offset_y=40.0)

    def drawBackground(self, painter: QPainter, rect):
        super().drawBackground(painter, rect)

        grid_size = 20
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        lines_fine = []
        lines_thick = []

        for x in range(left, int(rect.right()), grid_size):
            if x % (grid_size * 5) == 0:
                lines_thick.append((x, rect.top(), x, rect.bottom()))
            else:
                lines_fine.append((x, rect.top(), x, rect.bottom()))

        for y in range(top, int(rect.bottom()), grid_size):
            if y % (grid_size * 5) == 0:
                lines_thick.append((rect.left(), y, rect.right(), y))
            else:
                lines_fine.append((rect.left(), y, rect.right(), y))

        painter.setPen(QPen(QColor("#2A2A2A"), 1.0))
        for line in lines_fine:
            painter.drawLine(line[0], line[1], line[2], line[3])

        painter.setPen(QPen(QColor("#1E1E1E"), 1.5))
        for line in lines_thick:
            painter.drawLine(line[0], line[1], line[2], line[3])
