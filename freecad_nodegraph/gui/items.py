"""QGraphicsItem representations for Sockets, Edges, and Nodes."""

import sys
try:
    from PySide6.QtWidgets import (
        QGraphicsItem,
        QGraphicsTextItem,
        QGraphicsPathItem,
        QGraphicsProxyWidget,
        QGraphicsDropShadowEffect,
        QStyleOptionGraphicsItem,
        QWidget,
        QLineEdit,
        QCheckBox,
        QLabel,
        QHBoxLayout,
        QVBoxLayout,
        QMenu,
    )
    from PySide6.QtCore import Qt, QPointF, QRectF, QPoint
    from PySide6.QtGui import (
        QPen,
        QBrush,
        QColor,
        QPainter,
        QPainterPath,
        QFont,
        QLinearGradient,
        QAction,
        QCursor,
    )
except ImportError:
    try:
        from PySide2.QtWidgets import (
            QGraphicsItem,
            QGraphicsTextItem,
            QGraphicsPathItem,
            QGraphicsProxyWidget,
            QGraphicsDropShadowEffect,
            QStyleOptionGraphicsItem,
            QWidget,
            QLineEdit,
            QCheckBox,
            QLabel,
            QHBoxLayout,
            QVBoxLayout,
            QMenu,
        )
        from PySide2.QtCore import Qt, QPointF, QRectF, QPoint
        from PySide2.QtGui import (
            QPen,
            QBrush,
            QColor,
            QPainter,
            QPainterPath,
            QFont,
            QLinearGradient,
            QAction,
            QCursor,
        )
    except ImportError:
        from PyQt5.QtWidgets import (
            QGraphicsItem,
            QGraphicsTextItem,
            QGraphicsPathItem,
            QGraphicsProxyWidget,
            QGraphicsDropShadowEffect,
            QStyleOptionGraphicsItem,
            QWidget,
            QLineEdit,
            QCheckBox,
            QLabel,
            QHBoxLayout,
            QVBoxLayout,
            QMenu,
            QAction,
        )
        from PyQt5.QtCore import Qt, QPointF, QRectF, QPoint
        from PyQt5.QtGui import (
            QPen,
            QBrush,
            QColor,
            QPainter,
            QPainterPath,
            QFont,
            QLinearGradient,
            QCursor,
        )

from typing import TYPE_CHECKING, Optional
from freecad_nodegraph.core.socket import DataType

if TYPE_CHECKING:
    from freecad_nodegraph.core.socket import Socket
    from freecad_nodegraph.core.node import BaseNode
    from freecad_nodegraph.core.edge import Edge

# Color palette mapping for DataType
SOCKET_TYPE_COLORS = {
    DataType.FLOAT: QColor("#A6E22E"),      # Lime Green
    DataType.INT: QColor("#66D9EF"),        # Cyan
    DataType.STRING: QColor("#E6DB74"),     # Yellow
    DataType.BOOLEAN: QColor("#AE81FF"),    # Purple
    DataType.VECTOR: QColor("#FD971F"),     # Orange
    DataType.PLACEMENT: QColor("#F92672"),  # Pink / Magenta
    DataType.SHAPE: QColor("#2196F3"),      # Blue
    DataType.OBJECT: QColor("#00ACC1"),     # Teal
    DataType.ANY: QColor("#B0BEC5"),        # Light Gray
}


class GraphicsSocketItem(QGraphicsItem):
    """Visual graphics item for a node socket."""

    def __init__(self, socket: "Socket", parent: "GraphicsNodeItem"):
        super().__init__(parent)
        self.socket = socket
        self.node_item = parent
        self.radius = 6.5

        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
        self.setAcceptHoverEvents(True)
        self.setToolTip(f"{self.socket.name} ({self.socket.data_type.value})")

    def get_color(self) -> QColor:
        return SOCKET_TYPE_COLORS.get(self.socket.data_type, QColor("#B0BEC5"))

    def boundingRect(self) -> QRectF:
        r = self.radius + 4
        return QRectF(-r, -r, 2 * r, 2 * r)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        painter.setRenderHint(QPainter.Antialiasing)

        color = self.get_color()
        if self.socket.is_connected:
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
        else:
            painter.setBrush(QBrush(QColor("#222222")))
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

            # Dynamic edge color matching start socket type
            color = start_item.get_color()
            self.pen.setColor(color)
            self.setPen(self.pen)

        path = QPainterPath(start_pos)
        dx = end_pos.x() - start_pos.x()

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
        self.width = 180.0
        self.height = 100.0

        self.socket_items = {}
        self.label_items = []

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
        self.create_inline_input_widgets()

    def recalculate_size(self):
        num_inputs = len(self.node.inputs)
        num_outputs = len(self.node.outputs)

        if getattr(self.node, "category", "") == "Input":
            if hasattr(self.node, "set_components") or hasattr(self.node, "set_position"):
                self.height = 115.0
                self.width = 180.0
            else:
                self.height = 75.0
                self.width = 180.0
            return

        max_socks = max(num_inputs, num_outputs, 1)

        self.height = 35 + max_socks * 24 + 10

        # Calculate width needed for longest socket labels
        max_in_len = max([len(s.name) for s in self.node.inputs] or [0])
        max_out_len = max([len(s.name) for s in self.node.outputs] or [0])
        title_len = len(self.node.title)

        calculated_width = max(180.0, (max_in_len + max_out_len + 4) * 8.0, title_len * 9.0)
        self.width = calculated_width

    def create_sockets(self):
        label_font = QFont("Arial", 8, QFont.Bold)

        # Input Sockets and Labels
        for i, sock in enumerate(self.node.inputs):
            item = GraphicsSocketItem(sock, self)
            y_pos = 40 + i * 24
            item.setPos(0, y_pos)
            self.socket_items[sock] = item

            txt = QGraphicsTextItem(sock.name, self)
            txt.setDefaultTextColor(QColor("#E0E0E0"))
            txt.setFont(label_font)
            txt.setPos(12, y_pos - 10)
            self.label_items.append(txt)

        # Output Sockets and Labels
        for i, sock in enumerate(self.node.outputs):
            item = GraphicsSocketItem(sock, self)
            y_pos = 40 + i * 24
            item.setPos(self.width, y_pos)
            self.socket_items[sock] = item

            txt = QGraphicsTextItem(sock.name, self)
            txt.setDefaultTextColor(QColor("#E0E0E0"))
            txt.setFont(label_font)
            txt.setPos(self.width - txt.boundingRect().width() - 12, y_pos - 10)
            self.label_items.append(txt)

    def create_inline_input_widgets(self):
        """Create embedded PySide inline widgets with real-time error checking for Input nodes."""
        if getattr(self.node, "category", "") != "Input":
            return

        node = self.node
        valid_style = "border: 1px solid #555555; background-color: #222222; color: #A6E22E; font-weight: bold;"
        error_style = "border: 2px solid #FF5252; background-color: #381A1A; color: #FFD2D2;"

        # FloatNode, IntegerNode, StringNode
        if hasattr(node, "set_value") and not hasattr(node, "set_components"):
            if node.node_type == "BooleanNode":
                cb = QCheckBox("True")
                cb.setChecked(getattr(node, "value", False))
                cb.setStyleSheet("color: #AE81FF; font-weight: bold;")

                def on_toggle(checked):
                    node.set_value(checked)

                cb.toggled.connect(on_toggle)

                proxy = QGraphicsProxyWidget(self)
                proxy.setWidget(cb)
                proxy.setPos(15, 40)
            else:
                line_edit = QLineEdit(str(getattr(node, "value", "")))
                line_edit.setMaximumWidth(110)
                line_edit.setStyleSheet(valid_style)

                def on_text_changed(txt):
                    try:
                        node.set_value(txt)
                        line_edit.setStyleSheet(valid_style)
                        line_edit.setToolTip("")
                    except ValueError as err:
                        line_edit.setStyleSheet(error_style)
                        line_edit.setToolTip(str(err))

                line_edit.textChanged.connect(on_text_changed)

                proxy = QGraphicsProxyWidget(self)
                proxy.setWidget(line_edit)
                proxy.setPos(15, 40)

        # VectorNode & PlacementNode
        elif hasattr(node, "set_components") or hasattr(node, "set_position"):
            setter = getattr(node, "set_components", getattr(node, "set_position", None))

            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(2)

            curr_x = getattr(node, "x", getattr(node, "pos_x", 0.0))
            curr_y = getattr(node, "y", getattr(node, "pos_y", 0.0))
            curr_z = getattr(node, "z", getattr(node, "pos_z", 0.0))

            vals = {"x": curr_x, "y": curr_y, "z": curr_z}

            for comp in ["X", "Y", "Z"]:
                row = QHBoxLayout()
                row.setContentsMargins(0, 0, 0, 0)
                lbl = QLabel(f"{comp}:")
                lbl.setStyleSheet("color: #FD971F; font-weight: bold;")
                edit = QLineEdit(str(vals[comp.lower()]))
                edit.setMaximumWidth(75)
                edit.setStyleSheet(valid_style)

                def make_comp_handler(c_name, le):
                    def handler(txt):
                        try:
                            val_f = float(txt)
                            vals[c_name.lower()] = val_f
                            setter(**{c_name.lower(): val_f})
                            le.setStyleSheet(valid_style)
                            le.setToolTip("")
                        except ValueError:
                            le.setStyleSheet(error_style)
                            le.setToolTip(f"Invalid float for {c_name}: '{txt}'")
                    return handler

                edit.textChanged.connect(make_comp_handler(comp, edit))

                row.addWidget(lbl)
                row.addWidget(edit)
                layout.addLayout(row)

            proxy = QGraphicsProxyWidget(self)
            proxy.setWidget(container)
            proxy.setPos(15, 38)

    def contextMenuEvent(self, event):
        """Handle secondary (right-click) context menu on node."""
        menu = QMenu()

        cut_act = menu.addAction("Cut")
        copy_act = menu.addAction("Copy")
        paste_act = menu.addAction("Paste")
        duplicate_act = menu.addAction("Duplicate")
        menu.addSeparator()
        detach_act = menu.addAction("Detach Links")

        scene = self.scene()
        if not scene or not hasattr(scene, "clipboard_data"):
            paste_act.setEnabled(False)
        elif not scene.clipboard_data:
            paste_act.setEnabled(False)

        pos = event.screenPos().toPoint() if hasattr(event.screenPos(), "toPoint") else QCursor.pos()
        selected_action = menu.exec_(pos)

        if selected_action == cut_act:
            if scene and hasattr(scene, "cut_selected_nodes"):
                if not self.isSelected():
                    self.setSelected(True)
                scene.cut_selected_nodes()
        elif selected_action == copy_act:
            if scene and hasattr(scene, "copy_selected_nodes"):
                if not self.isSelected():
                    self.setSelected(True)
                scene.copy_selected_nodes()
        elif selected_action == paste_act:
            if scene and hasattr(scene, "paste_nodes"):
                scene.paste_nodes()
        elif selected_action == duplicate_act:
            if scene and hasattr(scene, "duplicate_selected_nodes"):
                if not self.isSelected():
                    self.setSelected(True)
                scene.duplicate_selected_nodes()
        elif selected_action == detach_act:
            if scene and hasattr(scene, "detach_node_links"):
                scene.detach_node_links(self.node)

        event.accept()

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
