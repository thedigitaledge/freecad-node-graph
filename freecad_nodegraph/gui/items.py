"""QGraphicsItem representations for Sockets, Edges, and Nodes."""

import sys
try:
    from PySide6.QtWidgets import (
        QGraphicsItem,
        QGraphicsTextItem,
        QGraphicsPathItem,
        QGraphicsDropShadowEffect,
        QStyleOptionGraphicsItem,
        QWidget,
    )
    from PySide6.QtCore import Qt, QPointF, QRectF
    from PySide6.QtGui import (
        QPen,
        QBrush,
        QColor,
        QPainter,
        QPainterPath,
        QFont,
        QLinearGradient,
    )
except ImportError:
    try:
        from PySide2.QtWidgets import (
            QGraphicsItem,
            QGraphicsTextItem,
            QGraphicsPathItem,
            QGraphicsDropShadowEffect,
            QStyleOptionGraphicsItem,
            QWidget,
        )
        from PySide2.QtCore import Qt, QPointF, QRectF
        from PySide2.QtGui import (
            QPen,
            QBrush,
            QColor,
            QPainter,
            QPainterPath,
            QFont,
            QLinearGradient,
        )
    except ImportError:
        from PyQt5.QtWidgets import (
            QGraphicsItem,
            QGraphicsTextItem,
            QGraphicsPathItem,
            QGraphicsDropShadowEffect,
            QStyleOptionGraphicsItem,
            QWidget,
        )
        from PyQt5.QtCore import Qt, QPointF, QRectF
        from PyQt5.QtGui import (
            QPen,
            QBrush,
            QColor,
            QPainter,
            QPainterPath,
            QFont,
            QLinearGradient,
        )

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from freecad_nodegraph.core.socket import Socket
    from freecad_nodegraph.core.node import BaseNode
    from freecad_nodegraph.core.edge import Edge


class GraphicsSocketItem(QGraphicsItem):
    """Visual graphics item for a node socket."""

    def __init__(self, socket: "Socket", parent: "GraphicsNodeItem"):
        super().__init__(parent)
        self.socket = socket
        self.node_item = parent
        self.radius = 6.0

        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
        self.setAcceptHoverEvents(True)

    def boundingRect(self) -> QRectF:
        r = self.radius + 3
        return QRectF(-r, -r, 2 * r, 2 * r)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        painter.setRenderHint(QPainter.Antialiasing)

        color = QColor("#4CAF50") if self.socket.is_input else QColor("#2196F3")
        if self.socket.is_connected:
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
        else:
            painter.setBrush(QBrush(QColor("#2C2C2C")))
            painter.setPen(QPen(color, 2.0))

        painter.drawEllipse(
            QPointF(0, 0), self.radius, self.radius
        )

    def get_scene_pos(self) -> QPointF:
        return self.scenePos()


class GraphicsEdgeItem(QGraphicsPathItem):
    """Visual graphics item for a connection edge."""

    def __init__(self, edge: "Edge", parent=None):
        super().__init__(parent)
        self.edge = edge
        self.setZValue(-1)

        self.pen = QPen(QColor("#FF9800"), 2.5, Qt.SolidLine)
        self.pen.setCapStyle(Qt.RoundCap)
        self.setPen(self.pen)

    def update_path(self, start_pos: QPointF = None, end_pos: QPointF = None):
        if not start_pos or not end_pos:
            if not self.edge.start_socket or not self.edge.end_socket:
                return

            scene = self.scene()
            if not scene:
                return

            start_item = scene.get_socket_item(self.edge.start_socket)
            end_item = scene.get_socket_item(self.edge.end_socket)

            if not start_item or not end_item:
                return

            start_pos = start_item.get_scene_pos()
            end_pos = end_item.get_scene_pos()

        path = QPainterPath(start_pos)
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()

        ctrl_offset = max(abs(dx) * 0.5, 40)

        c1 = QPointF(start_pos.x() + ctrl_offset, start_pos.y())
        c2 = QPointF(end_pos.x() - ctrl_offset, end_pos.y())

        path.cubicTo(c1, c2, end_pos)
        self.setPath(path)


class GraphicsNodeItem(QGraphicsItem):
    """Visual graphics item for a node."""

    def __init__(self, node: "BaseNode"):
        super().__init__()
        self.node = node
        self.width = 160.0
        self.height = 100.0

        self.socket_items = {}

        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemSendsGeometryChanges
        )

        self.init_ui()

    def init_ui(self):
        self.setPos(self.node.pos_x, self.node.pos_y)

        # Title text item
        self.title_item = QGraphicsTextItem(self.node.title, self)
        self.title_item.setDefaultTextColor(QColor("#FFFFFF"))
        font = QFont("Arial", 10, QFont.Bold)
        self.title_item.setFont(font)
        self.title_item.setPos(10, 5)

        self.recalculate_size()
        self.create_sockets()

    def recalculate_size(self):
        num_inputs = len(self.node.inputs)
        num_outputs = len(self.node.outputs)
        max_socks = max(num_inputs, num_outputs, 1)

        self.height = 35 + max_socks * 24 + 10
        self.width = max(160.0, len(self.node.title) * 9.0)

    def create_sockets(self):
        for i, sock in enumerate(self.node.inputs):
            item = GraphicsSocketItem(sock, self)
            y_pos = 40 + i * 24
            item.setPos(0, y_pos)
            self.socket_items[sock] = item

            # Label text
            txt = QGraphicsTextItem(sock.name, self)
            txt.setDefaultTextColor(QColor("#CCCCCC"))
            txt.setFont(QFont("Arial", 8))
            txt.setPos(12, y_pos - 10)

        for i, sock in enumerate(self.node.outputs):
            item = GraphicsSocketItem(sock, self)
            y_pos = 40 + i * 24
            item.setPos(self.width, y_pos)
            self.socket_items[sock] = item

            # Label text
            txt = QGraphicsTextItem(sock.name, self)
            txt.setDefaultTextColor(QColor("#CCCCCC"))
            txt.setFont(QFont("Arial", 8))
            txt.setPos(self.width - txt.boundingRect().width() - 12, y_pos - 10)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        painter.setRenderHint(QPainter.Antialiasing)

        # Body rectangle
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, 8, 8)

        # Background color
        body_color = QColor("#353535")
        if self.isSelected():
            pen_color = QColor("#FFA726")
            pen_width = 2.5
        else:
            pen_color = QColor("#555555")
            pen_width = 1.5

        painter.setPen(QPen(pen_color, pen_width))
        painter.setBrush(QBrush(body_color))
        painter.drawPath(path)

        # Header bar
        header_path = QPainterPath()
        header_path.addRoundedRect(0, 0, self.width, 30, 8, 8)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#252525")))
        painter.drawPath(header_path)

        # Divider line
        painter.setPen(QPen(QColor("#555555"), 1.0))
        painter.drawLine(0, 30, self.width, 30)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            self.node.pos_x = value.x()
            self.node.pos_y = value.y()
            if self.scene():
                self.scene().update_node_edges(self)
        return super().itemChange(change, value)
