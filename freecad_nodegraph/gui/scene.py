"""QGraphicsScene for rendering and interacting with the NodeGraph."""

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

from typing import Dict, Optional
from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.node import BaseNode
from freecad_nodegraph.core.socket import Socket
from freecad_nodegraph.core.edge import Edge
from freecad_nodegraph.gui.items import (
    GraphicsNodeItem,
    GraphicsSocketItem,
    GraphicsEdgeItem,
)


class NodeGraphicsScene(QGraphicsScene):
    """Graphics scene managing node items, edges, grid drawing and interaction."""

    def __init__(self, graph: Graph, parent=None):
        super().__init__(parent)
        self.graph = graph

        self.node_items: Dict[BaseNode, GraphicsNodeItem] = {}
        self.edge_items: Dict[Edge, GraphicsEdgeItem] = {}
        self.socket_item_map: Dict[Socket, GraphicsSocketItem] = {}

        self.drag_start_socket: Optional[Socket] = None
        self.drag_edge_item: Optional[QGraphicsPathItem] = None

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
